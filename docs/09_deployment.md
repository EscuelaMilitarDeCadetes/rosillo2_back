# Despliegue

## Estructura de settings

`config/settings/` está dividido por ambiente, todos heredan de `base.py`:

- `base.py` — apps instaladas, middleware, DB, DRF, JWT, Axes, CORS, reCAPTCHA, sesiones, logging. Lee todo lo sensible desde `.env` (vía `python-dotenv`).
- `local.py` — `DEBUG=True`, `ALLOWED_HOSTS=['localhost', '127.0.0.1']`, HTTPS/HSTS desactivados. Para desarrollo en máquina local.
- `development.py` — igual a `local.py` pero `ALLOWED_HOSTS` viene de la variable de entorno `ALLOWED_HOSTS`. Pensado para un ambiente de desarrollo compartido/remoto.
- `stage.py` — `DEBUG=False`, fuerza `SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE`, pero **HSTS sigue en 0** (a propósito, para no forzar HTTPS permanentemente mientras se prueba en stage).
- `production.py` — `DEBUG=False`, todo el endurecimiento de seguridad activo: HSTS a 1 año con subdominios y preload, `X_FRAME_OPTIONS="DENY"`, cookies `HttpOnly`, `SECURE_PROXY_SSL_HEADER` para operar detrás de proxy/load balancer.

`manage.py`, `wsgi.py` y `asgi.py` apuntan por defecto a `config.settings.local`. **Al desplegar hay que cambiar `DJANGO_SETTINGS_MODULE`** (o exportar la variable de entorno) al módulo correcto (`config.settings.stage` o `config.settings.production`) — esto no ocurre automáticamente.

## Variables de entorno (`.env`)

Cargadas por `base.py` desde `BASE_DIR / '.env'`. Como mínimo se requieren:

- `SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `ALLOWED_HOSTS` (en `development`/`stage`/`production`)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`
- `DOCUMENTOS_ROOT` (opcional, default `C:\RUTA_DOCUMENTOS_ROSILLO`)

## Base de datos

PostgreSQL, configurada 100% por variables de entorno (`DATABASES['default']` en `base.py`). No hay `sqlite` de respaldo — todos los ambientes, incluido local, requieren Postgres corriendo.

## Colas de tareas (Celery)

El envío de correo (`EmailService`) y el job diario de recordatorios de tareas (`enviar_recordatorios_tareas_task`) corren como tareas asíncronas vía Celery, con Redis como broker y result backend.

- `config/celery.py` define la app de Celery (`app = Celery('rosillo')`), autodescubre tareas (`apps.common.tasks`, y cualquier `tasks.py` que se agregue en otros módulos).
- `config/__init__.py` importa la app de Celery al arrancar Django.
- `CELERY_BEAT_SCHEDULE` (en `base.py`) programa `enviar_recordatorios_tareas_task` todos los días a las 7:00 a.m. Se usa un diccionario estático en settings en vez de `django-celery-beat`, para no agregar tablas nuevas (fase de modelado de BD cerrada).
- En `local.py`, `CELERY_TASK_ALWAYS_EAGER = True` hace que las tareas corran en el mismo proceso durante desarrollo y `python manage.py test apps` — **no requiere Redis levantado para correr la suite de tests**. En `stage`/`production` esta variable no debe estar activa: ahí se necesita worker real.
- En `local.py`, `CHANNEL_LAYERS` usa `channels.layers.InMemoryChannelLayer` en vez del `RedisChannelLayer` de `base.py`, por la misma razón que `CELERY_TASK_ALWAYS_EAGER`: evitar que la suite de tests (o cualquier test que use `captureOnCommitCallbacks(execute=True)`) dependa de un Redis real levantado. En `stage`/`production` se hereda el `RedisChannelLayer` de `base.py` sin cambios.

**Procesos requeridos en despliegue (además de Django/ASGI):**

```bash
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

Ambos requieren acceso a la misma instancia de Redis configurada en `CELERY_BROKER_URL`.

## Archivos estáticos y media

- `STATIC_ROOT = BASE_DIR / 'staticfiles'` — requiere `collectstatic` antes de servir en stage/producción (no hay configuración de `whitenoise` ni CDN todavía).
- `MEDIA_ROOT = BASE_DIR / 'media'` y `DOCUMENTOS_ROOT` (ver `04_document_management.md`) son rutas de disco separadas de `MEDIA_ROOT` — hay que asegurarse de que existan y tengan permisos de escritura en el servidor destino.


## Pasos de despliegue (checklist)

1. Configurar `.env` del ambiente destino.
2. `DJANGO_SETTINGS_MODULE=config.settings.<ambiente>`
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput`
5. Levantar `celery worker` y `celery beat` (ver sección "Colas de tareas" arriba) — sin esto, los correos quedan encolados sin enviarse y el job de recordatorios no corre.
6. Levantar ASGI (`config.asgi.application`) con `daphne` (ver Dockerfile/docker-compose) + proxy (nginx).
7. Verificar que `DOCUMENTOS_ROOT` y sus subcarpetas existen y son escribibles por el usuario del proceso.


## Decisiones ya resueltas

- **Dockerfile / docker-compose / CI**: agregados (`Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`). El CI corre la suite completa de tests en cada push/PR, sin necesitar Redis (`CELERY_TASK_ALWAYS_EAGER=True` en `local.py`).
- **`CORS_ALLOWED_ORIGINS` parametrizado por ambiente**: ver `07_security.md`.
- **`SECURE_HSTS_SECONDS` configurable vía `.env`**: permite subirlo gradualmente en producción sin redeploy — ver detalle arriba.