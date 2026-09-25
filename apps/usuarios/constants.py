# apps/usuarios/constants.py
"""
Clasificación de roles de plataforma por tipo de vínculo institucional
que requieren al ser asignados a un usuario.

Única fuente de verdad: antes vivía duplicada en
apps.integracion.services.vinculacion_service, en
ReemplazarUsuarioModal.js y en AddRoleModal.js (frontend). Ahora esos
tres lugares leen de aquí (los dos backend) o del campo calculado
'tipo_vinculacion' que RolPlataformaSerializer expone a partir de estas
mismas constantes (los dos frontend).

Vive en usuarios y no en integracion porque RolPlataforma es un modelo
de usuarios; integracion depende de usuarios, no al revés.
"""
ROLES_CON_FACULTAD = {'DECANO', 'FACULTAD', 'ESTUDIANTE', 'JURADO', 'TUTOR'}
ROLES_CON_GRUPO = {'GRUPO', 'CINTERNO', 'CEXTERNO', 'ASESOR'}


def tipo_vinculacion(nombre_rol: str) -> str | None:
    """Devuelve 'facultad', 'grupo' o None según el nombre del rol."""
    nombre = (nombre_rol or '').upper()
    if nombre in ROLES_CON_FACULTAD:
        return 'facultad'
    if nombre in ROLES_CON_GRUPO:
        return 'grupo'
    return None