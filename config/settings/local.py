from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# El valor de DEBUG se leerá como un string 'True' o 'False', lo comparamos.
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Seguridad HTTPS
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# HSTS
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

CELERY_TASK_ALWAYS_EAGER = True

# Igual que con Celery: en desarrollo/tests no hay Redis levantado.
# InMemoryChannelLayer resuelve group_send en el mismo proceso, sin
# depender de un broker real — necesario para que
# captureOnCommitCallbacks(execute=True) pueda ejecutar el push de
# NotificacionService.crear() sin romper cuando se corre la suite de tests.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')