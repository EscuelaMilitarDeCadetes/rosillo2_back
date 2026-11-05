from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'

    def ready(self):
        import apps.common.signals  # noqa: F401

        # Tareas diarias (recordatorios, integridad de documentos) dentro
        # del mismo proceso del servidor, sin celery beat.
        from apps.common import programador
        programador.iniciar()
