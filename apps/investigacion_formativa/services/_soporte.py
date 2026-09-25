"""
Utilidades internas compartidas por los *_service.py de investigacion_formativa
para (a) resolver el/los Usuario(s) destino de una Notificacion, (b) detectar
si el ejecutor de una accion tiene el rol de plataforma FACULTAD, de cara al
flujo de aprobacion de Decano, y (c) autorizar acciones sobre InstanciaEtapa
contra el rol_responsable configurado en EtapaFlujo. No expone endpoints ni
es una capa del patron de 5 capas: es soporte interno, igual que
apps/common/signals.py.
"""
import logging

from apps.common.services.notificacion_service import NotificacionService
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def usuario_id_de_persona(persona):
    """Retorna el id del Usuario actualmente asignado a una Persona
    (UsuarioXPersona.estado=True), o None si no tiene asignacion activa."""
    if persona is None:
        return None
    asignacion = persona.asignaciones.filter(estado=True).first()
    return asignacion.usuario_id if asignacion else None


def persona_actual_de_usuario(usuario):
    """Retorna la Persona actualmente asignada a un Usuario
    (UsuarioXPersona.estado=True), o None si no tiene asignacion activa.
    Es el inverso de `usuario_id_de_persona`."""
    if usuario is None or not getattr(usuario, "is_authenticated", True):
        return None
    asignacion = usuario.asignaciones.filter(estado=True).first()
    return asignacion.persona if asignacion else None


def usuario_id_estudiante_de_proceso(proceso_formativo):
    """Retorna el id del Usuario del estudiante activo (ParticipanteProceso,
    rol_en_modalidad='ESTUDIANTE', activo=True) de un ProcesoFormativo."""
    from apps.investigacion_formativa.models import ParticipanteProceso
    participante = (
        ParticipanteProceso.objects
        .filter(proceso_formativo=proceso_formativo, rol_en_modalidad='ESTUDIANTE', activo=True)
        .select_related('persona')
        .first()
    )
    if participante is None:
        return None
    return usuario_id_de_persona(participante.persona)


def usuarios_ids_participantes_de_proceso(proceso_formativo, roles):
    """Retorna la lista de ids de Usuario de los participantes activos de un
    ProcesoFormativo cuyo rol_en_modalidad este en `roles` (iterable de str,
    ej. ['ESTUDIANTE', 'TUTOR', 'JURADO']). Ignora participantes sin Usuario
    activo asignado."""
    from apps.investigacion_formativa.models import ParticipanteProceso
    participantes = (
        ParticipanteProceso.objects
        .filter(proceso_formativo=proceso_formativo, rol_en_modalidad__in=roles, activo=True)
        .select_related('persona')
    )
    ids = []
    for participante in participantes:
        usuario_id = usuario_id_de_persona(participante.persona)
        if usuario_id:
            ids.append(usuario_id)
    return ids


def notificar(usuario_destino_id, mensaje, tipo='info', url_relacionada=None):
    """Envia una Notificacion (con correo) si hay un destinatario valido.
    Nunca propaga una excepcion: un fallo de notificacion no debe revertir
    la transaccion de negocio (aprobacion, asignacion, etc.) que la origina."""
    if not usuario_destino_id:
        return None
    try:
        return NotificacionService.crear(
            usuario_destino_id=usuario_destino_id,
            mensaje=mensaje,
            tipo=tipo,
            url_relacionada=url_relacionada,
            notificar_email=True,
        )
    except Exception:
        logger.exception(
            "No se pudo crear la Notificacion para usuario_destino_id=%s: %s",
            usuario_destino_id, mensaje,
        )
        return None


def notificar_varios(usuario_ids, mensaje, tipo='info', url_relacionada=None):
    """Igual que `notificar`, pero para una lista de destinatarios."""
    for usuario_id in usuario_ids:
        notificar(usuario_id, mensaje, tipo=tipo, url_relacionada=url_relacionada)


def ejecutor_es_facultad(ejecutor):
    """True si el Usuario ejecutor tiene el rol de plataforma FACULTAD activo
    (misma consulta que apps.usuarios.permissions.es_facultad.EsFacultad,
    pero como logica de negocio de servicio, no como permiso de vista)."""
    from apps.usuarios.models import RolXUsuario
    return RolXUsuario.objects.filter(
        usuario=ejecutor, rol__nombre_rol='FACULTAD', estado=True,
    ).exists()


def ejecutor_es_decano_o_soporte(ejecutor):
    """True si el Usuario ejecutor tiene el rol de plataforma DECANO o SOPORTE
    activo. Estos dos roles ya tienen acceso administrativo total sobre el
    modulo (ver ROLES_ESCRITURA_GESTION en permissions.py) y por eso actuan
    como 'superusuarios' del motor de flujo: pueden resolver cualquier etapa
    sin importar a que rol este asignada."""
    from apps.usuarios.models import RolXUsuario
    return RolXUsuario.objects.filter(
        usuario=ejecutor, rol__nombre_rol__in=('DECANO', 'SOPORTE'), estado=True,
    ).exists()


def ejecutor_autorizado_para_etapa(instancia, ejecutor):
    """True si `ejecutor` tiene realmente el rol que EtapaFlujo.rol_responsable
    exige para poder iniciar/aprobar/rechazar/pasar a segunda instancia esta
    InstanciaEtapa.
    - 'FACULTAD' es un rol de plataforma (no depende del proceso puntual):
      se valida con `ejecutor_es_facultad`, igual que en el resto de services
      que ya usan ese patron (evaluacion_proceso_service, evento_evaluativo_
      service, participante_proceso_service).
    - 'ESTUDIANTE' / 'TUTOR' / 'JURADO' son roles por proceso (ParticipanteProceso.
      rol_en_modalidad): se valida que el ejecutor sea la Persona activa con
      ese rol en el ProcesoFormativo especifico de la instancia, no un rol
      global de plataforma.
    - Decano y Soporte siempre estan autorizados (ver `ejecutor_es_decano_o_
      soporte`), consistente con que ya tienen acceso administrativo total al
      resto de acciones del modulo.
    """
    from apps.investigacion_formativa.models import ParticipanteProceso
    if ejecutor_es_decano_o_soporte(ejecutor):
        return True
    rol_responsable = instancia.etapa.rol_responsable
    if rol_responsable == 'FACULTAD':
        return ejecutor_es_facultad(ejecutor)
    persona = persona_actual_de_usuario(ejecutor)
    if persona is None:
        return False
    return ParticipanteProceso.objects.filter(
        proceso_formativo=instancia.proceso,
        persona=persona,
        rol_en_modalidad=rol_responsable,
        activo=True,
    ).exists()
    
def ejecutor_es_gestor_administrativo(ejecutor):
    """True si el ejecutor tiene rol Facultad, Decano o Soporte: los tres
    roles que la Historia de Usuario habilita para 'gestionar en nombre de'
    un estudiante (crear/editar/eliminar registros que no son propios)."""
    return ejecutor_es_facultad(ejecutor) or ejecutor_es_decano_o_soporte(ejecutor)

def validar_ejecutor_autor_o_gestor(persona_autor_id, ejecutor, entidad="este registro"):
    """Verifica que `ejecutor` sea la Persona autora/responsable directa del
    registro (comparando contra su Persona actualmente asignada), o que
    tenga un rol administrativo (Facultad/Decano/Soporte) que le permita
    actuar en su nombre. Lanza PermissionDenied en caso contrario.
    Usar cuando el modelo expone directamente el FK a Persona responsable
    (ej. ActividadFormativa.responsable, PostulacionProceso.estudiante.persona)."""
    if ejecutor_es_gestor_administrativo(ejecutor):
        return
    persona = persona_actual_de_usuario(ejecutor)
    if persona is None or persona.id != persona_autor_id:
        raise PermissionDenied(
            f"Solo la persona autora de {entidad}, o un gestor administrativo "
            "(Facultad/Decano/Soporte), puede realizar esta acción."
        )

def validar_ejecutor_autor_o_gestor_por_proceso(proceso_formativo, ejecutor, entidad="este registro"):
    """Igual que `validar_ejecutor_autor_o_gestor`, pero para modelos que no
    tienen un FK directo a Persona y en cambio cuelgan de un ProcesoFormativo
    (ej. CertificacionExterna.proceso): resuelve al estudiante activo de ese
    proceso vía `usuario_id_estudiante_de_proceso`."""
    if ejecutor_es_gestor_administrativo(ejecutor):
        return
    usuario_id_estudiante = usuario_id_estudiante_de_proceso(proceso_formativo)
    if usuario_id_estudiante is None or usuario_id_estudiante != ejecutor.id:
        raise PermissionDenied(
            f"Solo el estudiante autor de {entidad}, o un gestor administrativo "
            "(Facultad/Decano/Soporte), puede realizar esta acción."
        )
        
def validar_ejecutor_autor_directo_o_gestor(usuario_autor_id, ejecutor, entidad="este registro"):
    """Igual que `validar_ejecutor_autor_o_gestor`, pero para modelos que
    referencian directamente al Usuario autor (no a su Persona), como
    RegistroActividades.registrado_por."""
    if ejecutor_es_gestor_administrativo(ejecutor):
        return
    if usuario_autor_id != ejecutor.id:
        raise PermissionDenied(
            f"Solo quien registró {entidad}, o un gestor administrativo "
            "(Facultad/Decano/Soporte), puede realizar esta acción."
        )