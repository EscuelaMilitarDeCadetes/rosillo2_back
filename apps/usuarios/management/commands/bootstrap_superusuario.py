"""
Carga el superusuario inicial desde el fixture `superusuario_inicial.json`
SOLO si aún no existe ningún superusuario en la base de datos.

Es IDEMPOTENTE: se puede ejecutar en cada despliegue (entrypoint de Docker,
pipeline de CI/CD, script manual) sin riesgo de duplicar, sobrescribir ni
tocar el superusuario una vez que ya existe.

Requisito: el archivo superusuario_inicial.json (generado con
`python manage.py dumpdata usuarios.Usuario --pks=1 --indent=2`)
debe estar en la raíz del proyecto (junto a manage.py), la misma
ubicación donde lo exportaste.
"""
#apps/usuarios/management/commands/bootstrap_superusuario.py
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

Usuario = get_user_model()

FIXTURE_PATH = Path(settings.BASE_DIR) / "superusuario_inicial.json"


class Command(BaseCommand):
    help = (
        "Carga el superusuario inicial desde superusuario_inicial.json, "
        "únicamente si no existe ningún superusuario en la base de datos."
    )

    def handle(self, *args, **options):
        # 1. Si ya existe cualquier superusuario, no tocamos nada.
        if Usuario.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(
                    "Ya existe al menos un superusuario en esta base de datos. "
                    "No se carga el fixture."
                )
            )
            return

        # 2. Verificamos que el fixture exista antes de intentar cargarlo.
        if not FIXTURE_PATH.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"No se encontró el fixture en {FIXTURE_PATH}. "
                    "Verifica que superusuario_inicial.json esté en la raíz "
                    "del proyecto antes de desplegar."
                )
            )
            return

        # 3. Cargamos el fixture (crea el usuario con el pk explícito, ej. 1).
        call_command("loaddata", str(FIXTURE_PATH))

        # 4. IMPORTANTE: loaddata inserta con el pk fijo del fixture pero NO
        #    avanza la secuencia SERIAL de PostgreSQL para esa tabla. Sin este
        #    ajuste, el próximo usuario creado normalmente por la aplicación
        #    podría chocar contra ese mismo id y fallar con IntegrityError.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval("
                "  pg_get_serial_sequence('auth_user', 'id'), "
                "  COALESCE((SELECT MAX(id) FROM auth_user), 1)"
                ")"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Superusuario inicial cargado desde fixture y secuencia de "
                "IDs de PostgreSQL corregida correctamente."
            )
        )