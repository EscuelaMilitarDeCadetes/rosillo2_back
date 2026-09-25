from django.conf import settings
from django.utils.module_loading import import_string

from apps.usuarios.services.interfaces import GestionUsuarioInterface

class UsuarioFacade:
    """
    Único punto de resolución hacia la implementación de GestionUsuarioInterface.
    apps.usuarios no importa apps.integracion en ningún lugar de su código;
    solo conoce el string de configuración GESTION_USUARIO_SERVICE.
    """

    @staticmethod
    def service() -> "GestionUsuarioInterface":
        service_class = import_string(settings.GESTION_USUARIO_SERVICE)
        return service_class()