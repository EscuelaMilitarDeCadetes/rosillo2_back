from django.http import JsonResponse


def lockout_response(request, credentials, *args, **kwargs):
    """
    Reemplaza AXES_LOCKOUT_TEMPLATE = 'lockout.html'.

    Por qué: settings/base.py tiene TEMPLATES.APP_DIRS=True y DIRS=[],
    pero este proyecto es una API pura (DRF) sin ninguna app que traiga
    una plantilla 'lockout.html'. Si django-axes bloquea a alguien tras
    AXES_FAILURE_LIMIT intentos fallidos e intenta renderizar esa
    plantilla, Django lanza TemplateDoesNotExist y lo que debería ser un
    403 controlado se convierte en un 500 real.

    Con este callable, el bloqueo se comporta igual que cualquier otro
    403 de la API: JSON plano, que el interceptor de axiosInstance.js ya
    sabe redirigir a /forbidden.
    """
    return JsonResponse(
        {"error": "Demasiados intentos fallidos. Tu cuenta quedó bloqueada temporalmente."},
        status=403,
    )