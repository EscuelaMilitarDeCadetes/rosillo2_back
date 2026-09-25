# E:\PROYECTO_ROSILLO\django_react\django\rosillo\apps\usuarios\ambitos.py
"""
Mapeo de qué roles institucionales pueden autenticarse en cada ámbito del
sistema (investigacion_formal / investigacion_formativa).

Este mapeo se construyó revisando qué clases EsX se usan realmente en
apps/investigacion_formal/permissions.py y apps/investigacion_formativa/
permissions.py (no es una lista inventada): Asesor, CExterno, CInterno y
Grupo solo participan en formal; Estudiante, Jurado y Tutor solo participan
en formativa; Decano, Facultad, Gerente, Soporte y Supervisor participan en
ambos y por lo tanto pueden loguearse indistintamente por cualquiera de los
dos endpoints.

No se guarda en BD (el modelo de datos está congelado): el ámbito viaja
únicamente como claim dentro del JWT, decidido en el momento del login.
"""

AMBITO_FORMAL = "formal"
AMBITO_FORMATIVA = "formativa"

ROLES_AMBITO_FORMAL = {
    "ASESOR", "CEXTERNO", "CINTERNO", "GRUPO",
    "DECANO", "FACULTAD", "GERENTE", "SOPORTE", "SUPERVISOR",
}

ROLES_AMBITO_FORMATIVA = {
    "ESTUDIANTE", "JURADO", "TUTOR",
    "DECANO", "FACULTAD", "GERENTE", "SOPORTE", "SUPERVISOR",
}

ROLES_POR_AMBITO = {
    AMBITO_FORMAL: ROLES_AMBITO_FORMAL,
    AMBITO_FORMATIVA: ROLES_AMBITO_FORMATIVA,
}


def usuario_tiene_acceso_a_ambito(usuario, ambito):
    """
    True si el usuario tiene al menos un rol activo (RolXUsuario.estado=True)
    entre los roles permitidos para el ambito solicitado.
    """
    from apps.usuarios.models import RolXUsuario

    roles_permitidos = ROLES_POR_AMBITO.get(ambito, set())
    if not roles_permitidos:
        return False

    return RolXUsuario.objects.filter(
        usuario=usuario,
        rol__nombre_rol__in=roles_permitidos,
        estado=True,
    ).exists()