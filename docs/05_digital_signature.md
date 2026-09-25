# Firma digital de documentos

La plataforma permite gestionar el ciclo de vida de firma de documentos institucionales de forma genérica: cualquier modelo de cualquier módulo puede requerir firma, sin necesidad de tablas o lógica específica por tipo de documento.

## Modelos utilizados (módulo `common`)

### `DocumentoFirma`

Representa un documento sometido a proceso de firma.

| Campo | Notas |
|---|---|
| `content_type` / `object_id` | `GenericForeignKey` — vincula el documento con el objeto de negocio al que pertenece (un `Proyecto`, una `Convocatoria`, un `TrabajoGrado`, etc.), `null=True, blank=True` con índice compuesto |
| `ruta_documento` | Ruta en disco del archivo. La base de datos **nunca** almacena el binario, solo la ruta |
| `estado` | `BORRADOR` → `EN_FIRMAS` → `FIRMADO` / `RECHAZADO` |
| `version` | Entero, se incrementa si el documento se reemplaza tras un rechazo o corrección |
| `hash_documento` | Hash del archivo, usado para verificar integridad y detectar si el archivo en disco cambió respecto al registrado |
| `habilitado_firma` | Booleano de control, permite pausar el proceso de firma sin cambiar el estado |

### `DocumentoFirmante`

Registra cada firmante requerido para un `DocumentoFirma`, su posición en el orden de firma y su estado individual.

| Campo | Notas |
|---|---|
| `documento` | FK a `DocumentoFirma` |
| `usuario` | Firmante asignado |
| `orden` | Posición en la secuencia de firma (entero) |
| `estado` | `PENDIENTE` → `FIRMADO` / `RECHAZADO` |
| `fecha_firma` | Se completa al firmar |
| `motivo_rechazo` | Obligatorio si `estado = RECHAZADO`; texto libre con la justificación del firmante |

## Flujo

1. **Generación del documento.** El documento físico se produce (a partir de una plantilla de `PlantillaDocumento` o cargado directamente) y se guarda en disco. `DocumentoFirmaService.crear()` registra la ruta con `estado='BORRADOR'` y calcula el `hash_documento`.
2. **Asignación de firmantes.** El rol responsable (`cinterno` o `facultad`, según el flujo) define quiénes deben firmar y en qué orden, creando los `DocumentoFirmante` correspondientes. El documento pasa a `estado='EN_FIRMAS'`.
3. **Firma secuencial.** Los firmantes solo pueden firmar respetando el `orden` definido — un firmante con `orden=2` no puede firmar mientras el de `orden=1` siga `PENDIENTE`. Cada firma exitosa marca ese `DocumentoFirmante` como `FIRMADO` y registra `fecha_firma`.
4. **Rechazo (camino alterno).** Cualquier firmante puede rechazar en su turno. El rechazo exige `motivo_rechazo` y el `DocumentoFirma` pasa a `estado='RECHAZADO'`. El proceso no continúa con los firmantes restantes: el documento debe corregirse y volver a someterse a firma, lo que genera una nueva `version`.
5. **Firma completa.** Cuando el último `DocumentoFirmante` en el orden firma, `DocumentoFirma.estado` pasa automáticamente a `FIRMADO`. Este es el punto donde, en el futuro, se podría disparar el movimiento del archivo a una ubicación de "documentos firmados" si se decide implementar esa segregación física (ver `04_document_management.md`).

## Auditoría

Cada cambio de estado — creación, asignación de firmantes, cada firma individual, cada rechazo — se registra vía `HistorialService.registrar()`, con `ejecutor` igual al usuario que ejecuta la acción (no necesariamente el firmante afectado, ya que quien asigna firmantes puede ser otro rol).

## Relación con otros módulos

`DocumentoFirma` usa el mismo patrón de `GenericForeignKey` que `Historial` y `Tarea` dentro de `common`, lo que permite que cualquier módulo (`investigacion_formal` e `investigacion_formativa`, que ya lo reutiliza en su flujo de inscripción, aprobación temática y actas) reutilice el sistema de firma sin declarar tablas propias. Ejemplos de objetos que hoy o a futuro requieren firma: actas de cierre de proyecto, fichas técnicas de seguimiento, formatos de inscripción y aprobación temática de trabajos de grado, certificados de cumplimiento.


## Decisiones ya resueltas

- **Escritura física del archivo a disco**: `DocumentoFirmaService.crear_desde_archivo()` centraliza la escritura del binario vía `default_storage.save()`, a partir de un archivo subido por multipart, para que ningún módulo reimplemente esa lógica. 
- **Notificación a firmantes**: `DocumentoFirmanteService.asignar_firmante()` y `generar_codigo_verificacion()` disparan `NotificacionService.crear(..., notificar_email=True)` automáticamente; el firmante ya no depende de revisar manualmente si tiene documentos pendientes.
- **Verificación de integridad periódica**: `DocumentoFirmaService.verificar_integridad_todos()` corre diariamente vía Celery Beat (`verificar_integridad_documentos_task`, 2:00 a.m.). Recalcula el hash de cada `DocumentoFirma` y lo compara contra `hash_documento` (calculado una única vez al crear el documento). Si no coincide o el archivo ya no existe en disco, se registra en `Historial` (ejecutor "SISTEMA") y se notifica por `NotificacionService` a todos los superusuarios activos, vía in-app y email.
