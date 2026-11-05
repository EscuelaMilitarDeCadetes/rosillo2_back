# apps/common/management/commands/verificar_integridad_documentos.py
"""
Equivalente a la tarea de Celery beat 'verificar-integridad-documentos-diario',
para correrla A MANO cuando se necesite (pruebas, o forzar una corrida).
La corrida automática diaria la hace apps/common/programador.py dentro del
mismo proceso de runserver; NO hace falta cron ni Programador de tareas:

    python manage.py verificar_integridad_documentos
"""
from django.core.management.base import BaseCommand

from apps.common.services.documento_firma_service import DocumentoFirmaService


class Command(BaseCommand):
    help = "Recalcula el hash de cada DocumentoFirma y alerta si hay discrepancias."

    def handle(self, *args, **options):
        r = DocumentoFirmaService.verificar_integridad_todos()
        self.stdout.write(self.style.SUCCESS(
            f"{r['verificados']} documentos verificados, {r['alterados']} con alerta."
        ))
