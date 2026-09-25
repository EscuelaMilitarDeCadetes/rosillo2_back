from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# El valor de DEBUG se leerá como un string 'True' o 'False', lo comparamos.
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Seguridad HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
# Arrancar bajo (ej. 3600 = 1 hora) en el primer despliegue, mientras se
# confirma que el certificado SSL es estable, y subir gradualmente hasta
# 31536000 (1 año) vía .env, sin necesidad de redeploy de código.
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Protección headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin"

# Cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1200
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')