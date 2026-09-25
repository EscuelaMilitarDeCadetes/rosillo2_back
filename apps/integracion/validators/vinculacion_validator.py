"""
Validador de integración.
"""
from rest_framework.exceptions import ValidationError

from apps.integracion.selectors.vinculacion_selector import VinculacionSelector


class VinculacionValidator:

    # ------------------------------------------------------------------ #
    # Datos obligatorios por flujo
    # ------------------------------------------------------------------ #
    @staticmethod
    def validar_datos_persona(data: dict):
        requeridos = ['grado_id', 'nombre', 'apellido', 'documento', 'celular', 'correo']
        for campo in requeridos:
            if not data.get(campo):
                raise ValidationError({campo: f"El campo '{campo}' es obligatorio."})

    @staticmethod
    def validar_datos_flujo_administrativo(data: dict):
        """Flujo 1: Persona + Usuario, sin PersonaXGrupo."""
        VinculacionValidator.validar_datos_persona(data)
        if not data.get('rol_plataforma_id'):
            raise ValidationError(
                {"rol_plataforma_id": "El rol de plataforma es obligatorio."}
            )

    @staticmethod
    def validar_datos_flujo_facultad(data: dict):
        """Flujo 2: Persona + Usuario + PersonaXGrupo(facultad)."""
        VinculacionValidator.validar_datos_persona(data)
        if not data.get('rol_plataforma_id'):
            raise ValidationError(
                {"rol_plataforma_id": "El rol de plataforma es obligatorio."}
            )
        if not data.get('facultad_id'):
            raise ValidationError(
                {"facultad_id": "La facultad es obligatoria para este tipo de usuario."}
            )
        if not data.get('rol_grupo_id'):
            raise ValidationError(
                {"rol_grupo_id": "El rol dentro de la facultad es obligatorio."}
            )

    @staticmethod
    def validar_datos_flujo_grupo(data: dict):
        """Flujo 3: Persona + Usuario + PersonaXGrupo(grupo)."""
        VinculacionValidator.validar_datos_persona(data)
        if not data.get('rol_plataforma_id'):
            raise ValidationError(
                {"rol_plataforma_id": "El rol de plataforma es obligatorio."}
            )
        if not data.get('grupo_id'):
            raise ValidationError(
                {"grupo_id": "El grupo de investigación es obligatorio para este tipo de usuario."}
            )
        if not data.get('rol_grupo_id'):
            raise ValidationError(
                {"rol_grupo_id": "El rol dentro del grupo es obligatorio."}
            )

    # ------------------------------------------------------------------ #
    # Reemplazo y retiro
    # ------------------------------------------------------------------ #
    @staticmethod
    def validar_reemplazo(usuario_id: int):
        if not VinculacionSelector.usuario_activo(usuario_id):
            raise ValidationError(
                f"El usuario id={usuario_id} no está activo o no existe. "
                f"No se puede reemplazar un usuario inactivo."
            )

    @staticmethod
    def validar_retiro(usuario_id: int):
        if not VinculacionSelector.usuario_activo(usuario_id):
            raise ValidationError(
                f"El usuario id={usuario_id} ya está inactivo."
            )
    
    @staticmethod
    def validar_persona_para_rol_institucional(usuario_id: int, persona, nombre_rol: str):
        """
        Usado por VinculacionService.asignar_rol_existente() cuando el rol
        a asignar pertenece a ROLES_CON_FACULTAD o ROLES_CON_GRUPO: ese tipo
        de rol no tiene sentido sin una Persona real detrás del Usuario.
        """
        if persona is None:
            raise ValidationError(
                f"El usuario id={usuario_id} no tiene una Persona activa "
                f"asignada (UsuarioXPersona). No se puede asignar el rol "
                f"'{nombre_rol}', que requiere vínculo institucional."
            )

    @staticmethod
    def validar_datos_asignacion_rol_existente(data: dict, requiere: str):
        """
        requiere: 'facultad' o 'grupo'.
        Mismos campos obligatorios que validar_datos_flujo_facultad()/
        validar_datos_flujo_grupo(), pero sin exigir los datos de Persona
        (el usuario y la persona ya existen).
        """
        if not data.get('rol_grupo_id'):
            raise ValidationError(
                {"rol_grupo_id": "El rol dentro de la facultad/grupo es obligatorio."}
            )
        if requiere == 'facultad' and not data.get('facultad_id'):
            raise ValidationError(
                {"facultad_id": "La facultad es obligatoria para este tipo de rol."}
            )
        if requiere == 'grupo' and not data.get('grupo_id'):
            raise ValidationError(
                {"grupo_id": "El grupo de investigación es obligatorio para este tipo de rol."}
            )