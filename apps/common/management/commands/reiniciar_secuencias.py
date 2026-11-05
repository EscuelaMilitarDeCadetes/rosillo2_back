# apps/common/management/commands/reiniciar_secuencias.py
"""
Detecta (y opcionalmente corrige) las secuencias de IDs de PostgreSQL que
quedaron desfasadas.

Síntoma: listar y editar registros funciona, pero al CREAR uno nuevo sale
error 500 con "llave duplicada viola restricción de unicidad «..._pkey»".

Causa: se insertaron filas indicando el id a mano (restaurar un backup,
pgAdmin, un INSERT con id, loaddata, un script de carga...). PostgreSQL no
adelanta la secuencia en esos casos, así que el siguiente id que propone ya
existe.

Uso:
    python manage.py reiniciar_secuencias            -> sólo muestra cuáles están mal
    python manage.py reiniciar_secuencias --aplicar  -> además las corrige

Corregir es seguro: sólo mueve la secuencia al id más alto que ya existe en
la tabla; no modifica ni borra datos. Se puede correr cuantas veces se quiera.
"""
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Revisa y corrige secuencias de IDs desfasadas en PostgreSQL (error 500 al crear registros)."

    def add_arguments(self, parser):
        parser.add_argument('--aplicar', action='store_true',
                            help='Corrige las secuencias desfasadas (sin esto sólo las muestra).')

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            raise CommandError("Este comando sólo aplica a PostgreSQL.")

        aplicar = options['aplicar']
        q = connection.ops.quote_name
        revisadas, desfasadas = 0, []

        tablas_vistas = set()
        with connection.cursor() as cursor:
            for model in apps.get_models(include_auto_created=True):
                if model._meta.proxy or not model._meta.managed:
                    continue
                tabla = model._meta.db_table
                pk = model._meta.pk
                if tabla in tablas_vistas or pk is None:
                    continue
                tablas_vistas.add(tabla)
                if pk.get_internal_type() not in ('AutoField', 'BigAutoField', 'SmallAutoField'):
                    continue

                cursor.execute("SELECT pg_get_serial_sequence(%s, %s)", [q(tabla), pk.column])
                fila = cursor.fetchone()
                secuencia = fila[0] if fila else None
                if not secuencia:
                    continue

                cursor.execute(f"SELECT last_value, is_called FROM {secuencia}")
                last_value, is_called = cursor.fetchone()
                siguiente = last_value + 1 if is_called else last_value

                cursor.execute(f"SELECT MAX({q(pk.column)}) FROM {q(tabla)}")
                maximo = cursor.fetchone()[0]
                revisadas += 1

                if maximo is not None and maximo >= siguiente:
                    desfasadas.append((tabla, secuencia, siguiente, maximo))

            if not desfasadas:
                self.stdout.write(self.style.SUCCESS(
                    f"{revisadas} tablas revisadas: todas las secuencias están bien."))
                return

            self.stdout.write(self.style.WARNING(
                f"{len(desfasadas)} de {revisadas} tablas tienen la secuencia desfasada "
                f"(crear registros en ellas puede dar error 500):"))
            for tabla, _, siguiente, maximo in desfasadas:
                self.stdout.write(f"  - {tabla}: el próximo id sería {siguiente}, pero ya existe hasta el {maximo}")

            if not aplicar:
                self.stdout.write("\nPara corregirlas ejecuta:  python manage.py reiniciar_secuencias --aplicar")
                return

            with transaction.atomic():
                for tabla, secuencia, _, maximo in desfasadas:
                    cursor.execute("SELECT setval(%s, %s, true)", [secuencia, maximo])
            self.stdout.write(self.style.SUCCESS(
                f"\nListo: {len(desfasadas)} secuencias corregidas. Ya se pueden crear registros."))
