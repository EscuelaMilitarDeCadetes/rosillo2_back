from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import NotFound


def custom_exception_handler(exc, context):
    """
    Extiende el exception_handler por defecto de DRF para que cualquier
    Model.DoesNotExist (lanzado por los Selectors, según la convención
    'obtener(id) - lanza excepción si no existe' de 11_backend_logic.md)
    se traduzca a un 404 limpio en vez de propagarse como un 500 genérico.

    Se aplica a nivel global (REST_FRAMEWORK['EXCEPTION_HANDLER']) para
    cubrir de una sola vez todos los módulos ya migrados, no solo crm.
    """
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound(detail="El recurso solicitado no existe.")

    return drf_exception_handler(exc, context)