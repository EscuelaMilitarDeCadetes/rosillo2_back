# apps/common/management/commands/enviar_recordatorios_tareas.py
"""
Equivalente a la tarea de Celery beat 'enviar-recordatorios-tareas-diario',
para correrla A MANO cuando se necesite (pruebas, o forzar una corrida).
La corrida automática diaria la hace apps/common/programador.py dentro del
mismo proceso de runserver; NO hace falta cron ni Programador de tareas:

    python manage.py enviar_recordatorios_tareas
    python manage.py enviar_recordatorios_tareas --dias 5
"""
from django.core.management.base import BaseCommand

from apps.common.services.notificacion_service import NotificacionService


class Command(BaseCommand):
    help = "Genera notificaciones (y correos) de tareas vencidas o próximas a vencer."

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=3,
                            help='Días de anticipación para avisar (por defecto 3).')

    def handle(self, *args, **options):
        creadas = NotificacionService.enviar_recordatorios_tareas(dias_anticipacion=options['dias'])
        self.stdout.write(self.style.SUCCESS(f"{len(creadas)} notificaciones generadas."))
