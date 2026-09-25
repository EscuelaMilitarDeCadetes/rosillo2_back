# API REST

La API se organiza por módulos, cada uno montado bajo su propio prefijo en `config/urls.py` y con un `DefaultRouter` interno (`urls.py` de cada app) que registra un recurso por `ViewSet`. Todos los `ViewSet` heredan de `viewsets.ViewSet` puro (ver `11_backend_logic.md`), así que junto a cada recurso CRUD conviven varias acciones (`@action`) que no siguen el verbo/URL estándar de un `ModelViewSet`.

La tabla resume el tamaño real de la superficie de API por módulo (recursos base registrados en el router + acciones `@action` adicionales), verificado en la auditoría de integración Django → React más reciente de cada grupo de módulos:

| Módulo | Prefijo | Recursos base | Acciones (`@action`) |
|---|---|---|---|
| `usuarios` | `/api/usuarios/` | — | 27 endpoints en total (incluye auth, password y roles-usuario) |
| `institucional` | `/api/institucional/` | — | 27 endpoints en total |
| `integracion` | `/api/integracion/` | — | 15 endpoints en total (sin tablas propias, ver `01_architecture.md`) |
| `crm` | `/api/crm/` | 3 | 8 |
| `common` | `/api/common/` | 9 | 30 |
| `investigacion_formal` | `/api/investigacion-formal/` | 19 | 64 |
| `investigacion_formativa` | `/api/investigacion-formativa/` | 27 | 111 |

`usuarios`, `institucional` e `integracion` combinan varios `router.register()` con vistas sueltas (login, password, token refresh, `me/`) por lo que se reportan como total de endpoints en vez de separar recursos base de acciones. Los conteos de `crm`, `common`, `investigacion_formal` e `investigacion_formativa` están confirmados con consumidor real en React (100% de paridad en los cuatro). `investigacion_formativa` fue el último módulo auditado, sus 27 recursos y 111 acciones tienen consumidor real en React, sin excepciones — con esto, los siete módulos del proyecto quedan con auditoría Django ↔ React cerrada y sin hallazgos abiertos.

## Usuarios (`/api/usuarios/`)

CRUD de `usuarios/`, `roles/`, `roles-usuario/`, `usuario-persona/`; acciones de activar/desactivar usuario, roles activos, histórico de asignación, reasignación y rotaciones; endpoints de autenticación (`login/formal/`, `login/formativa/`, `logout/`, `token/refresh/`, `me/`) y de contraseña (`password/forgot-password/`, `password/reset-password/`, `password/change-password/`). Incluye `usuarios/creados-por-mi/` y `usuarios/buscar/` (ver `07_security.md` para el detalle de los dos logins por ámbito).

## Institucional (`/api/institucional/`)

CRUD de `personas/`, `grados/`, `grupos/`, `facultades/`, `facultad-grupo/`, `persona-grupo/`, `roles-grupo/`, `gerentes/`; acciones de traslado y cambio de rol dentro de un grupo, consultas por usuario/facultad/persona, histórico de vinculación de una persona, gerente actual/histórico y `institucional/personas/buscar/` (selector paginado server-side para dropdowns de `Persona`).

## Integración (`/api/integracion/`)

No declara modelos propios (ver `01_architecture.md`): expone acciones de creación de usuarios por rol (`crear-soporte/`, `crear-supervisor/`, `crear-gerente/`, `crear-decano/`, `crear-facultad/`, `crear-grupo/`, `crear-cinterno/`, `crear-cexterno/`, `crear-asesor/`) más `reemplazar/`, `retirar/` y `asignar-rol-existente/`, junto con `crear-estudiante/`, `crear-jurado/` y `crear-tutor/` (protegidos con el permiso `EsFacultad` + `TieneAmbitoFormativa`).

## CRM (`/api/crm/`)

3 recursos base — `entidad-externa/`, `indicador-impacto/`, `interaccion/` — con 8 acciones de filtro (por tipo de relación, sector, país, entidad, proyecto, medio) y actualización de avance de indicadores.

## Common (`/api/common/`)

9 recursos base — `aprobacion/`, `documento-firma/`, `documento-firmante/`, `historial/`, `notificacion/`, `plantilla-documento/`, `soporte/`, `tarea/`, `tipos-documento/` — con 30 acciones (flujo de aprobación con turnos, firma secuencial, generación de código de verificación, bitácora, recordatorios de tareas, etc.). `soporte/` solo expone `create` por diseño (tickets de soporte). Ver `05_digital_signature.md` y `08_notifications.md` para el detalle de flujo de cada recurso.

## Investigación formal (`/api/investigacion-formal/`)

19 recursos base — `calificaciones/`, `control-cambios/`, `convocatorias/`, `ejecuciones/`, `estadisticas/`, `montos/`, `objetivos/`, `objetivo-punto/`, `productos-grupo/`, `productos-proyecto/`, `proyectos/`, `proyecto-convocatoria/`, `tipos-calificacion/`, `tipos-producto/`, `tipos-rubro/`, `puntos-control/`, `investigadores/`, `grupos-minciencias/`, `productos-minciencias/`, `roles-investigador/` — con 64 acciones adicionales (calificación por fases, exportación a Excel/PDF de `proyecto-convocatoria/`, avance presupuestal y ponderado, timeline, etc.). `puntos-control/` es de solo lectura (list/retrieve/create, sin update/destroy) por decisión de diseño. `objetivos/especificos/{proyecto_id}/` fue retirado del backend: React ya cubría ese caso vía `por-proyecto/{id}/`.

## Investigación formativa (`/api/investigacion-formativa/`)

27 recursos base registrados en el router — `actividad-formativa/`, `banco-ideas/`, `certificacion-externa/`, `estadisticas/`, `estudiante/`, `etapa-flujo/`, `evaluacion-proceso/`, `evento-evaluativo/`, `flujo-proceso/`, `homologacion/`, `instancia-etapa/`, `modalidad-facultad/`, `modalidad/`, `participante-proceso/`, `plan-trabajo/`, `postulacion-proceso/`, `proceso-formativo-proyecto/`, `proceso-formativo/`, `registro-actividades/`, `registro-horas/`, `regla-flujo/`, `requisito-modalidad/`, `revision/`, `segunda-instancia/`, `transicion-flujo/`, `tutor/`, `validacion-antiplagio/` — con 111 acciones adicionales que cubren el motor de flujo de trabajo parametrizable (transiciones, reglas, instancias de etapa), el ciclo de vida de cada `ProcesoFormativo` (postulación → aprobación → seguimiento → evaluación → cierre), la segunda instancia, el registro de horas/actividades y un bloque de estadísticas (`estadisticas/`) equivalente al de `investigacion_formal`. Reutiliza `DocumentoFirma`/`DocumentoFirmante` de `common` para las firmas del flujo (formatos de inscripción, aprobación temática, actas) y `HistorialService.registrar()` en cada mutación, siguiendo el mismo patrón que el resto de módulos (ver `11_backend_logic.md`).