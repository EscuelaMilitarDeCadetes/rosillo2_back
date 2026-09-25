# Lógica de backend: patrón de capas

Este documento describe el patrón arquitectónico que se aplicó de forma consistente en los siete módulos del backend (`usuarios`, `institucional`, `integracion`, `crm`, `common`, `investigacion_formal` e `investigacion_formativa`). 
No describe reglas de negocio puntuales de cada módulo (eso está en `01_architecture.md` y en los documentos de cada módulo), sino la convención de código en sí.

## Las cinco capas

Cada modelo con lógica de negocio tiene, dentro de su app, hasta cinco archivos/carpetas:

```
<app>/
  selectors/<modelo>_selector.py
  validators/<modelo>_validator.py
  serializers/<modelo>_serializer.py
  services/<modelo>_service.py
  views/<modelo>_viewset.py
```

### 1. Selectors — solo lectura

Encapsulan *cómo* se consulta, nunca reglas de negocio ni permisos. Interfaz estándar:

- `listar()`
- `obtener(id)` — lanza excepción si no existe
- `buscar(id)` — retorna `None` si no existe (variante silenciosa de `obtener`)
- `obtener_por_<campo>()`
- `existe_<campo>()`

### 2. Validators — reglas de datos/negocio, sin permisos

Los permisos **nunca** se validan aquí (eso es responsabilidad de la vista vía `get_permissions()`). Interfaz estándar:

- `validar_creacion(data)`
- `validar_actualizacion(instancia, data)`
- `validar_eliminacion(instancia)`
- Helpers privados `_validar_algo()` para reglas específicas reutilizadas internamente.

Cuando un validador necesita referenciar un modelo de otro módulo (FK cruzada), el import se hace **dentro del método**, no a nivel de archivo, para evitar ciclos de importación entre apps.

### 3. Serializers — uno por modelo

Sin lógica de negocio. Validaciones de formato (`DRF Field` validators) sí pueden vivir aquí; validaciones de negocio, no.

### 4. Services — orquestación + efectos secundarios

Todo lo que modifica estado pasa por aquí. Interfaz estándar:

- `listar()`, `obtener()`, `crear()`, `actualizar()`, `eliminar()` + métodos de negocio específicos (p. ej. `VinculacionService.vincular_por_grupo()`).
- Todo método de escritura está decorado con `@transaction.atomic`.
- Toda mutación termina llamando a `HistorialService.registrar(ejecutor, descripcion, objeto=None)`. `ejecutor` es siempre `request.user` (quien ejecuta la acción), no el usuario afectado por el cambio.
- `eliminar()` se **omite por completo** (ni en validator ni en service) para modelos sin campo `estado`/`activo` — no existe borrado simbólico donde no hay un campo que lo represente. Ejemplo en `investigacion_formal`: `GrupoMinciencias`, `Monto`, `ProductoMinciencias`, `ProductoXGrupo`, `RolInvestigador`, `TipoCalificacion`, `TipoProducto`, `TipoRubro`.

### 5. Views/ViewSets — adaptador HTTP puro

Heredan de `viewsets.ViewSet` (**no** `ModelViewSet`) — sin `queryset` automático, todo delegado al service. Responsabilidades exclusivas de esta capa:

- Parsear el request y llamar al service correspondiente.
- Definir permisos vía `get_permissions()` según el rol (`EsCInterno`, `EsFacultad`, `EsSoporte`, etc.), nunca dentro del service.
- Serializar la respuesta.
- **Cero lógica de negocio.** Si una vista empieza a tener `if`s sobre reglas de negocio, esa lógica debe subir al service o al validator.

Al usar `viewsets.ViewSet` sin `queryset`, `router.register()` **requiere `basename` explícito** — omitirlo rompe el registro de URLs silenciosamente en algunos casos y siempre es un `AssertionError` en otros.

## Auditoría (`Historial`)

- `HistorialService.registrar(ejecutor, descripcion, objeto=None)` se llama en cada mutación de cualquier módulo.
- `Historial` es **append-only**: el modelo no expone `actualizar()` ni `eliminar()`.
- Campos opcionales `campo`, `valor_anterior`, `valor_nuevo` (JSONField) permiten guardar diffs estructurados cuando se necesita trazabilidad fina (no todos los `registrar()` los usan).
- `Historial` usa `GenericForeignKey` (`content_type`/`object_id`), igual que `DocumentoFirma` y `Tarea` — mismo patrón reutilizado tres veces en `common`.
- Mismo criterio se aplicó al envío de correo: `EmailService.enviar()` (`apps/common/services/email_service.py`) es el único punto de entrada permitido para enviar email desde cualquier módulo — ningún service debe llamar a `send_mail()` ni a la tarea de Celery directamente.

## Borrado: soft-delete vs. hard-delete

No hay una regla única global; es una decisión por modelo, documentada explícitamente para evitar inconsistencias:

| Caso | Estrategia |
|---|---|
| Catálogos (`GradoEstudios`, `RolGrupo`, `GrupoInvestigacion`, `FacultadEscuela`, catálogos de `investigacion_formal`) | Permanentes, **sin endpoint de borrado** |
| `Persona` | Permanente; retiros se modelan con `PersonaXGrupo.estado`/`desvinculacion`, nunca borrando la persona |
| `Gerente` | Soft-delete (`estado=False`) |
| `EntidadExterna`, `IndicadorImpacto`, `Interaccion` (CRM) | Hard-delete (decisión institucional explícita) |
| `EntidadExterna` | Borrado bloqueado si tiene `Interaccion` asociadas |
| `ControlCambios` | Sin `estado`; el registro es append-only, solo se permiten togglear 4 flags booleanos |
| `Convocatoria` | Nunca se edita ni se borra; único cambio permitido es el toggle de estado, exclusivo de `CINTERNO` |
| Modelos sin `estado`/`activo` en `investigacion_formal` (ver lista arriba) | Sin `eliminar()` en absoluto |

La autenticación y seguridad de usuarios se documenta ahora en 07_security.md.

## Testing

- Los tests viven a nivel de **service**, no de vista (`APIClient` no se usa).
- Cada módulo tiene un `base.py` compartido con mixins de fixtures reutilizables entre archivos de test del mismo módulo.
- La validación de endpoints HTTP completos (incluyendo permisos, serialización, URLs) se hace aparte, con Postman, no con `APIClient` de DRF.

## Errores conocidos a vigilar al escribir código nuevo

- **Definiciones duplicadas de métodos en Python se descartan en silencio** (la segunda sobrescribe la primera sin error) — requiere auditar los archivos de service línea por línea, especialmente después de copiar/pegar entre módulos similares.
- Los hacks de IDs hardcodeados del Thymeleaf original (`grupo_id=3`, `id != 15`, segmentación fija Refimil/Ginsi/CM) están completamente abandonados; cualquier lógica nueva debe ser paramétrica sobre el esquema institucional genérico (`FacultadXGrupo` como fuente de verdad para la correspondencia grupo-facultad).
- Cualquier test que dependa de que un email se envíe (via assert sobre mail.outbox o sobre un mock de send_mail) debe envolver la llamada en self.captureOnCommitCallbacks(execute=True), y el @patch debe apuntar a apps.common.tasks.send_mail — nunca al módulo del service que originalmente llamaba a send_mail antes de la migración a Celery.