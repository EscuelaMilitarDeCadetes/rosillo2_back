# apps\investigacion_formativa\permissions.py
from apps.usuarios.permissions import (
    EsEstudiante, EsTutor, EsJurado, EsFacultad, EsDecano, EsSoporte,
)


def combinar(clases_permiso):
    """Combina varias clases de permiso DRF en un OR lógico (idéntico al
    'combinar' de investigacion_formal): basta con cumplir una de ellas."""
    class _Combinado:
        def __init__(self):
            self._instancias = [cls() for cls in clases_permiso]

        def has_permission(self, request, view):
            return any(p.has_permission(request, view) for p in self._instancias)

        def has_object_permission(self, request, view, obj):
            return any(
                getattr(p, 'has_object_permission', lambda *a: True)(request, view, obj)
                for p in self._instancias
            )
    return _Combinado()


# ---------------------------------------------------------------------------
# Genéricos (ya existían)
# ---------------------------------------------------------------------------

# Lectura amplia: cualquier rol con interés legítimo en ver el estado del flujo
ROLES_LECTURA_INVESTIGACION_FORMATIVA = [
    EsEstudiante, EsTutor, EsJurado, EsFacultad, EsDecano, EsSoporte
]

# Gestión administrativa/operativa del catálogo y de las asignaciones
ROLES_ESCRITURA_GESTION = [EsFacultad, EsDecano, EsSoporte]

# Creación operativa (asignar tutores/jurados a un proceso, programar eventos,
# registrar evaluaciones): Facultad puede crear directamente — el gateo hacia
# Decano ocurre DENTRO del service (ejecutor_es_facultad), no aquí.
ROLES_CREACION_OPERATIVA = [EsFacultad, EsDecano, EsSoporte]

# El propio estudiante autor de su plan de trabajo, o quien lo gestiona
ROLES_AUTOR_PLAN_TRABAJO = [EsEstudiante, EsFacultad, EsDecano]

# Aprobación/rechazo del plan de trabajo: quien lo evalúa, no quien lo escribe
ROLES_APROBACION_PLAN_TRABAJO = [EsTutor, EsFacultad, EsDecano]

# ---------------------------------------------------------------------------
# Ya estaban importados por algunos ViewSets pero nunca se habían definido
# ---------------------------------------------------------------------------

# El propio estudiante autor de su postulación (crear/editar/enviar/eliminar
# en BORRADOR), o quien la gestiona en su nombre
ROLES_AUTOR_POSTULACION = [EsEstudiante, EsFacultad, EsDecano]

# Paso administrativo ENVIADA -> EN_VALIDACION (no es la decisión final)
ROLES_VALIDACION_POSTULACION = [EsFacultad, EsDecano, EsSoporte]

# Calificación/evaluación académica: quien pone el concepto, no quien administra
# (ProcesoFormativo.calificar, Revision.crear, SegundaInstancia.crear,
# EvaluacionProceso.crear)
ROLES_CALIFICACION_PROCESO = [EsTutor, EsJurado, EsFacultad, EsDecano]

# Configuración de catálogo de flujo (EtapaFlujo, FlujoProceso, TransicionFlujo,
# ReglaFlujo, RequisitoModalidad): solo administración, nunca estudiante/tutor/jurado
ROLES_CONFIGURACION_FLUJO = [EsFacultad, EsDecano, EsSoporte]

# El propio estudiante que reporta su actividad formativa, o quien la gestiona
ROLES_AUTOR_REGISTRO_ACTIVIDADES = [EsEstudiante, EsFacultad, EsDecano]

# Aprobación del registro de actividades: quien lo supervisa (tutor), no quien lo redacta
ROLES_APROBACION_REGISTRO_ACTIVIDADES = [EsTutor, EsFacultad, EsDecano]

# ---------------------------------------------------------------------------
# Nuevo: flujo Facultad -> Decano (Aprobacion)
# ---------------------------------------------------------------------------

# Decisión DIRECTA sobre postulaciones y activación de segunda instancia:
# ya NO incluye a Facultad — Facultad debe pasar por 'solicitar_*'.
ROLES_DECISION_DIRECTA_DECANO = [EsDecano, EsSoporte]

# Facultad abre la solicitud de aprobación hacia el Decano
ROLES_SOLICITUD_APROBACION_FACULTAD = [EsFacultad]

# Solo el Decano confirma o deniega una solicitud abierta por Facultad
ROLES_CONFIRMACION_DECANO = [EsDecano]

# ---------------------------------------------------------------------------
# Nuevo: los 10 ViewSets que hoy solo tienen IsAuthenticated() (ver nota abajo)
# ---------------------------------------------------------------------------

# ActividadFormativa: el propio estudiante reporta/completa su actividad y
# adjunta soporte, o Facultad/Decano/Soporte la gestionan en su nombre
ROLES_GESTION_ACTIVIDAD_FORMATIVA = [EsEstudiante, EsFacultad, EsDecano, EsSoporte]

# BancoIdeas: alta/edición del catálogo de ideas (banco de proyectos disponibles)
ROLES_GESTION_BANCO_IDEAS = [EsFacultad, EsDecano, EsSoporte]

# BancoIdeas: separar/tomar/liberar una idea es una acción del propio estudiante
ROLES_INTERACCION_BANCO_IDEAS = [EsEstudiante, EsFacultad, EsDecano, EsSoporte]

# CertificacionExterna: el propio estudiante sube su certificado, o Facultad/Decano en su nombre
ROLES_AUTOR_CERTIFICACION_EXTERNA = [EsEstudiante, EsFacultad, EsDecano]

# CertificacionExterna: validar_horas es un acto de verificación administrativa
ROLES_VALIDACION_CERTIFICACION_EXTERNA = [EsFacultad, EsDecano]

# Homologacion: el propio estudiante solicita, o Facultad/Decano en su nombre
ROLES_AUTOR_HOMOLOGACION = [EsEstudiante, EsFacultad, EsDecano]

# Homologacion: aprobar/rechazar/cargar-acta es una decisión administrativa
ROLES_DECISION_HOMOLOGACION = [EsFacultad, EsDecano]

# InstanciaEtapa: iniciar/cambiar-estado/finalizar depende de a quién
# corresponda esa etapa según EtapaFlujo.rol_responsable — el service ya
# valida que el ejecutor concreto coincida con ese rol; aquí solo se filtra
# a quienes PODRÍAN llegar a ser responsables de alguna etapa
ROLES_GESTION_INSTANCIA_ETAPA = [EsEstudiante, EsTutor, EsJurado, EsFacultad, EsDecano, EsSoporte]