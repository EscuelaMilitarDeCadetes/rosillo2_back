# Seguridad

## Autenticación

- **JWT** vía `rest_framework_simplejwt`. Access token de 30 minutos, refresh de 1 día, con rotación de refresh tokens activada.
- **Blacklist de tokens** en logout y en desactivación de usuario. La invalidación se hace iterando `OutstandingToken.objects.filter(user=user)` y ejecutando `BlacklistedToken.objects.get_or_create(token=token)` por cada uno — se prefiere este patrón sobre `RefreshToken().blacklist()` porque invalida **todas** las sesiones activas del usuario (todos sus refresh tokens vigentes), no solo la sesión desde la que se ejecuta la acción. Esto es clave para el caso de desactivación forzada de un usuario.
- **Login dual por ámbito**: existen dos endpoints de login, `login-formal` y `login-formativa`, ambos servidos por `AmbitoLoginView` (base común en `usuarios/views/ambito_login_view.py`) con dos subclases concretas. El ámbito (formal/formativa) al que puede acceder cada rol está mapeado en `ambitos.py`. **El gate de ámbito ocurre en el login, no en el recurso**: si el usuario no tiene ningún `RolXUsuario` asociado a ese ámbito, el login responde `403 Forbidden` con `{"error": ...}` y nunca llega a emitir un access/refresh token. Esto es una diferencia de comportamiento importante frente al modelo anterior (donde el 403 ocurría al intentar acceder al recurso, no al loguearse) — los tests que antes usaban el login solo como paso de setup para obtener un token deben usar `login-formal`/`login-formativa` explícitamente (ya no existe el nombre de URL genérico `login`).
- **`TieneAmbitoFormal` / `TieneAmbitoFormativa`**: clases de permiso DRF (`usuarios/permissions/tiene_ambito.py`) que se combinan con las clases de permiso por rol en `get_permissions()` de cada `ViewSet`, para confirmar que el token JWT corresponde al ámbito correcto del recurso que se está consultando.
- **`UsuarioXPersona`** es la tabla intermedia que permite que una cuenta institucional (p. ej. `director.facultad.ciencias@...`) persista aunque la `Persona` que ocupa ese cargo rote. El historial de quién ocupó el cargo y cuándo queda auditado ahí, no se pierde al reasignar la cuenta.

## Control de fuerza bruta y throttling

- **`django-axes`**: bloqueo tras 5 intentos fallidos de login, con cooloff de 1 hora antes de permitir reintentar. El contador se reinicia automáticamente tras un login exitoso.
- **Throttling de DRF** (independiente de Axes, actúa a nivel de framework):
  - `anon`: 20 peticiones/minuto
  - `user`: 100 peticiones/minuto
  - `login`: 5 peticiones/minuto, vía `LoginRateThrottle` personalizado
- La combinación Axes + throttle de login cubre dos escenarios distintos: Axes bloquea por credenciales incorrectas repetidas, el throttle limita la tasa de peticiones al endpoint de login independientemente de si las credenciales son correctas o no (protege contra scripts que golpean el endpoint aunque no estén "fallando" intentos registrables por Axes).
- **reCAPTCHA** en formularios sensibles del frontend (llaves configuradas vía `RECAPTCHA_PUBLIC_KEY` / `RECAPTCHA_PRIVATE_KEY`).

## Control de acceso y roles

Los roles `Estudiante`, `Jurado` y `Tutor` están definidos a nivel de dominio (rol dentro de `PersonaXGrupo` / `ParticipanteProceso`) pero todavía no tienen una clase de permiso DRF propia — su control de acceso se resuelve hoy mediante `TieneAmbitoFormal()` / `TieneAmbitoFormativa()` combinado con el rol de plataforma, no con una clase de permiso dedicada por rol como en el resto de `investigacion_formal`.

## Registro de auditoría

Toda mutación de cualquier módulo pasa por `HistorialService.registrar(ejecutor, descripcion, objeto=None)`. `Historial` es append-only (no expone `actualizar()` ni `eliminar()`) y usa `GenericForeignKey` para poder auditar cualquier modelo del sistema sin tablas de historial por módulo. `ejecutor` siempre es el usuario que ejecuta la acción (`request.user`), no el usuario afectado por el cambio — esto importa quede claro en logs donde un `Soporte` modifica datos de otra persona.

## Seguridad de transporte y cabeceras (por ambiente)

Configurado de forma incremental según el ambiente (ver `09_deployment.md` para el detalle completo):

- `local` / `development`: sin HTTPS forzado, para no bloquear el desarrollo.
- `stage`: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` activos; HSTS todavía desactivado a propósito mientras se valida el certificado.
- `production`: además de lo anterior, HSTS a 1 año con subdominios y preload, `X_FRAME_OPTIONS="DENY"`, cookies `HttpOnly`, y soporte para operar detrás de proxy vía `SECURE_PROXY_SSL_HEADER`.

## CORS

`CORS_ALLOWED_ORIGINS` está definido en `base.py` y heredado por todos los ambientes — actualmente apunta solo a `http://localhost:3000` (frontend React en desarrollo local). **Pendiente**: parametrizar por ambiente antes de desplegar a `stage`/`production`, para no dejar ese origen de desarrollo habilitado en producción ni bloquear el dominio real del frontend desplegado.

## Decisiones ya resueltas

- **`CORS_ALLOWED_ORIGINS` parametrizado por ambiente**: cada ambiente lee su propio valor desde `.env` (ver `09_deployment.md`). `base.py` ya no trae un default de desarrollo — si un ambiente no lo define, CORS queda cerrado por defecto (falla cerrado, no abierto).
- **Alertas de `Aprobacion`/`DocumentoFirmante` pendientes**: se resolvieron reutilizando el sistema de `Notificacion` existente (`tipo='alerta'` + email), no se construyó un mecanismo nuevo tipo Axes — ver `08_notifications.md`.