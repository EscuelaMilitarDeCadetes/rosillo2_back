# Modelo de base de datos

La plataforma cuenta actualmente con 68 tablas diseñadas y 84 en la base de datos.

Se organizan en los siguientes módulos.


### Módulo: `common` (8 tablas)
- `Aprobacion`:  Maneja una "aprobación pendiente" en una Tarea asignada a un usuario específico sobre un objeto específico.
- `DocumentoFirma`: Almacena el documento final firmado y su estado.
- `DocumentoFirmante`: Registra los firmantes requeridos para un documento, su orden y estado.
- `Historial`: Log de todas las acciones realizadas en el sistema, cada click a un boton debe dejar un registro en esta tabla.
- `Notificacion`: Funciona como un sistema de alertas dentro de la app.
- `PlantillaDocumento`: Almacena plantillas .docx para ser diligenciadas.
- `Tarea`: Asigna una acción ("TODO - Tienes que hacer esto"), el sistema las rastree, asigne y audite.
- `TipoDocumento`: Clasificación de documentos (acta, informe, etc.).


### Módulo: `crm` (3 tablas)
- `EntidadExterna`: Empresas, Universidades aliadas, ONGs (Base del CRM)
- `IndicadorImpacto`: Analítica y BI
- `Interaccion`: Historial de contactos (Core CRM)


### Módulo: `institucional` (8 tablas)
- `FacultadEscuela`: Maneja toda la información relevante de las facultades dentro de la institución
- `FacultadXGrupo`: Asocia cada una de las 7 facultades existentes con cada uno de los 3 grupos de investigación actuales
- `Gerente`:  Maneja la información diferencial de la persona que funge como gerente de todos los proyectos
- `GradoEstudios`: Maneja los istintos grados tanto militares como civiles
- `GrupoInvestigacion`: Maneja los datos de los distintos grupos de investigación que se crearon en la institución
- `PersonaXGrupo`: Maneja las distintas personas y su vinculación a uno de los grupos de investigación institucionales
- `Persona`: Maneja la información principal de cada persona
- `RolGrupo`: Roles que desempeña cada persona dentro de cada grupo

### Módulo: `integración` (0 tablas)

### Módulo: `investigacion_formal` (19 tablas)
- `Calificacion`: Maneja las calificaciones de las 6 fases de aprobación que tiene cada proyecto interno
- `ControlCambios`: Maneja la información diferencial de los controles de cambio que deben ir en los informes de seguimiento
- `Convocatoria`: Maneja toda la información relacionada con las convocatorias ya sean internas o externas
- `Ejecucion`: Maneja los datos sobre la ejecucion presupuestal de cada proyecto financiado
- `GrupoMinciencias`: Maneja la información basica de los diferentes grupos de productos que tiene minciencias
- `InvestigadorXProyecto`: Asocia cada investigador con un proyecto y su rol en el mismo
- `Monto`: Maneja la información sobre el dinero solicitado, aprobado, contrapartia, entre otros de cada proyecto financiado
- `ObjetivoXPunto`: Asocia cada punto de control con un objetivo
- `Objetivos`: Maneja cada objetivo general y especificos que tiene cada proyecto y su implementación en el mismo
- `ProductoMinciencias`: Maneja la información de los diferentes productos que tiene minciencias
- `ProductoXGrupo`: Asocia cada producto según minciencia con su grupo respectivo según esa institución
- `ProductoXProyecto`: Asocia cada proyecto con la producción esperada/prometida de cada uno
- `ProyectoXConvocatoria`: Asocia cada proyecto con una convocatoria
- `Proyecto`: Maneja la información de cada proyecto
- `PuntoControl`: Maneja la información de los distintos puntos de control
- `RolInvestigador`: Roles que puede tener un investigador en un proyecto
- `TipoCalificacion`: Maneja las diferentes fases de calificacion
- `TipoProducto`: Maneja los diferentes tipos de producto en los que se podria catalogar según minciencias
- `TipoRubro`: Maneja los diferentes rubros que puede tener una ejecución presupuestal


### Módulo: `investigacion_formativa` (26 tablas)
- `ActividadFormativa`: Maneja la informcióny los distintos estados de las actividades que se pueden realizar
- `BancoIdeas`: Maneja la información de las distintas ideas que pueen volverse procesos formativos
- `CertificacionExterna`: Son certificaciones externas que el estudiante obtiene en instituciones o cursos externos.
- `Estudiante`: Maneja la información de los estudiantes
- `EtapaFlujo`: Catálogo de pasos ordenados por Modalidad
- `EvaluacionProceso`: Maneja los conceptos emitidos por los jurados de las procesos formativos
- `EventoEvaluativo`: Capaz de representar: sustentación, defensa, socialización, pitch, entre otros.
- `FlujoProceso`: Permite cambiar el workflow de una modalidad sin afectar procesos activos.
- `Homologacion`: Formaliza el reconocimiento académico al finalizar ciertos procesos.
- `InstanciaEtapa`: Controla el estado real (Pendiente/En Proceso/Completada) de un proceso de grado en una etapa específica.
- `ModalidadXFacultad`: Asocia cada opcion de grado con la facultad que la tiene disponible
- `Modalidad`: Maneja la información de las distintas modalidades
- `ParticipanteProceso`: Maneja la informaión de los distintos actores que participan en los procesos formativos
- `PlanTrabajo`: Plan formal de actividades e hitos.
- `PostulacionProceso`: Captura la solicitud antes de que exista un ProcesoFormativo
- `ProcesoFormativoXProyecto`: Asocia las procesos formativos con un proyecto de investigación formal en caso de requerirlo
- `ProcesoFormativo`: Maneja la información de las distintas procesos formativos
- `RegistroActividades`: Registro periódico de avances genérico y específico
- `RegistroHoras`: Control acumulado de horas
- `ReglaFlujo`: Modela las reglas del negocio
- `RequsitoModalidad`: Centraliza las reglas de elegibilidad por modalidad en la BD, no en código.
- `Revision`: Controla las iteraciones de correcciones de documentos dentro de una misma etapa.
- `SegundaInstancia`: Funciona para contemplar los casos donde entra en vigor
- `TransicionFlujo`: Modela el flujo condicional
- `Tutor`: Maneja la información de los distintos tutores o docentes
- `ValidacionAntiplagio`: Registra los resultados del software antiplagio (Turnitin) y su aprobación.


### Módulo: `usuarios` (diseñado) (4 tablas)
- `RolPlataforma`: Roles generales de la aplicación (soporte, supervisor, etc.).
- `RolXUsuario`: Asigna un `RolPlataforma` a un `Usuario`.
- `UsuarioXPersona`: Registro histórico de qué `Persona` utiliza qué `Usuario` en un período de tiempo. 
- `Usuario`: Modelo principal de autenticación (hereda de AbstractUser).


### Módulo: `usuarios` (base de datos) (14 tablas)
- `RolPlataforma`: Roles generales de la aplicación (soporte, supervisor, etc.).
- `RolXUsuario`: Asigna un `RolPlataforma` a un `Usuario`.
- `UsuarioXPersona`: Registro histórico de qué `Persona` utiliza qué `Usuario` en un período de tiempo. 
- `auth_group_permissions`:Heredó de AbstractUser, cuyos campos son: id, group_id, permission_id.
- `auth_group`:Heredó de AbstractUser, cuyos campos son: id, name.
- `auth_user_groups`:Heredó de AbstractUser, cuyos campos son: id, usuario_id, group_id.
- `auth_user_user_permissions`:Heredó de AbstractUser, cuyos campos son: id, usuario_id, permission_id
- `auth_permission`:Heredó de AbstractUser, cuyos campos son: id, name, content_type_id, codename.
- `auth_user`:Heredó de AbstractUser, cuyos campos son: id, password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, token_recuperacion, token_creado_en, email.
- `django_admin_log`:Heredó de AbstractUser, cuyos campos son: id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id.
- `django_content_type`:Heredó de AbstractUser, cuyos campos son: id, app_label, model.
- `auth_token`:Heredó de AbstractUser, cuyos campos son: key, created, user_id.
- `token_blacklist_blacklistedtoken`:Heredó de AbstractUser, cuyos campos son: id, blacklisted_at, token_id.
- `token_blacklist_outstandingtoken`:Heredó de AbstractUser, cuyos campos son: id, token, created_at, expires_at, user_id, jti.


### Tablas adicionaciones creadas al migrar la base de datos (6 tablas)
- `authtoken_token`: Cuyos campos son: key, created, user_id.
- `django_session`: Cuyos campos son: session_key, session_data, expire_date.
- `django_migrations`: Cuyos campos son: id, app, name, applied.
- `axes_accessfailurelog`: Cuyos campos son: id, user_agent, ip_address, username, http_accept, path_info, attempt_time, locked_out.
- `axes_accesslog`: Cuyos campos son: id, user_agent, ip_address, username, http_accept, path_info, attempt_time, logout_time, session_hash.
- `axes_accessattempt`: Cuyos campos son: id, user_agent, ip_address, username, http_accept, path_info, attempt_time, get_data, post_data, failures_since_start.