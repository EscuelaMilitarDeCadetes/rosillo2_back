# Sistema de notificaciones

Sistema de alertas internas de la plataforma, complementario al envío de correo electrónico.
Vive en el módulo `common` (`Notificacion`, `NotificacionService`, `NotificacionSelector`, `NotificacionValidator`, `NotificacionViewSet`).

## Modelo: `Notificacion`

| Campo                     | Tipo                  | Notas |
| `usuario_destino`         | FK a `Usuario`        | destinatario |
| `mensaje`                 | TextField             | obligatorio |
| `tipo`                    | CharField             | `info`, `exito`, `alerta`, `error` (opcional) |
| `leido`                   | BooleanField          | default `False` |
| `fecha_creacion`          | DateTimeField         | `auto_now_add` |
| `url_relacionada`         | CharField(255)        | opcional, para deep-linking desde el frontend |

Ordenamiento por defecto: `-fecha_creacion`.

## Servicio: `NotificacionService`

- `crear(usuario_destino_id, mensaje, tipo=None, url_relacionada=None, notificar_email=False)`
- `marcar_leida(notificacion_id)`
- `marcar_todas_leidas(usuario_id)` → retorna cantidad actualizada
- `listar_por_usuario(usuario_id, solo_no_leidas=False)`
- `contar_no_leidas(usuario_id)`
- `eliminar(notificacion_id, ejecutor)` — registra en `Historial`
- `enviar_recordatorios_tareas(dias_anticipacion=3)`:
  - Recorre `Tarea` vencidas (`TareaSelector.listar_vencidas()`) y próximas a vencer (`listar_proximas_a_vencer()`).
  - Por cada una genera una `Notificacion` tipo `alerta` + intenta enviar email (`notificar_email=True`).
  - Evita duplicar el mismo aviso el mismo día para la misma tarea vía `NotificacionSelector.existe_recordatorio_hoy(usuario_id, url_relacionada, tipo='alerta')`.
  - Al finalizar registra un resumen en `Historial` con `usuario=None` (acción de sistema).

**Envío de correo**

`notificar_email=True` dispara `NotificacionService._enviar_email()`, que delega en `EmailService.enviar()` (`apps/common/services/email_service.py`) — servicio central de correo, con la misma responsabilidad que `HistorialService` tiene para auditoría: cualquier módulo que necesite enviar un correo pasa por aquí, no llama a `send_mail()` directamente.

`EmailService.enviar()` encola el envío como tarea de Celery (`apps/common/tasks.py::enviar_email_task`) y difiere el `.delay()` hasta `transaction.on_commit()` internamente, así el caller no necesita envolverlo. **El envío ya no es síncrono**: el request retorna sin esperar a que SMTP responda; un worker de Celery procesa la tarea aparte. Reintentos automáticos (hasta 3, con backoff de 60s) están configurados en la tarea; si todos los intentos fallan, se loguea el error en vez de romper el flujo que originó la notificación (mismo criterio de tolerancia a fallos que tenía el `try/except` anterior, pero ahora con visibilidad en logs en vez de fallo silencioso).

## Endpoints — `NotificacionViewSet` (`/api/common/notificacion/`)

- CRUD estándar (`list`, `retrieve`, `create`, `destroy`)
- `POST /marcar-leida/<id>/`
- `POST /marcar-todas-leidas/` (usa `request.user` si no se pasa `usuario_destino`)
- `GET /por-usuario/<usuario_id>/?solo_no_leidas=true`
- `GET /no-leidas/<usuario_id>/`
- `POST /enviar-recordatorios/` — restringido a IsAdminUser, dispara el job de recordatorios manualmente con dias_anticipacion opcional en el body. Complementa (no reemplaza) la ejecución automática diaria vía Celery beat — ver más abajo.

## Decisiones ya resueltas

- **Relación con `Aprobacion` / `DocumentoFirmante`**: resuelto. `AprobacionService.crear()` notifica al `usuario_revisor` cuando se genera una solicitud `PENDIENTE`; `DocumentoFirmanteService.asignar_firmante()` notifica al firmante asignado. Ambos usan `tipo='alerta'` + `notificar_email=True`, mismo patrón que los recordatorios de `Tarea`.
- **Notificaciones en tiempo real**: hay WebSockets/Channels. Ruta de implementación ya definida (Channels + Redis, reutilizando el broker de Celery) — ver detalle en la sección de arquitectura.