from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from apps.usuarios.models import RolXUsuario, RolPlataforma
from apps.usuarios.constants import tipo_vinculacion
from apps.usuarios.services.usuario_service import UsuarioService
from apps.common.services.historial_service import HistorialService
from django.db import transaction

User = get_user_model()


class RolXUsuarioService:

    @staticmethod
    @transaction.atomic
    def agregar_rol_a_usuario(usuario_id: int, rol_id: int, ejecutor=None) -> RolXUsuario:
        usuario = get_object_or_404(User, pk=usuario_id)
        rol = get_object_or_404(RolPlataforma, pk=rol_id)
        # Si el rol requiere vínculo institucional, este método por
        # sí solo NUNCA es un punto de entrada válido: no crea ni
        # actualiza el PersonaXGrupo correspondiente. El único camino
        # soportado para esos roles es
        # VinculacionService.asignar_rol_existente() (apps.integracion),
        # que crea/actualiza el vínculo institucional ANTES de llamar a
        # este método, dentro de la misma transacción atómica.
        if tipo_vinculacion(rol.nombre_rol) is not None:
            from apps.institucional.models import PersonaXGrupo
            persona = UsuarioService.obtener_persona_actual(usuario)
            tiene_vinculo_activo = (
                persona is not None
                and PersonaXGrupo.objects.filter(persona=persona, estado=True).exists()
            )
            if not tiene_vinculo_activo:
                raise ValidationError(
                    f"El rol '{rol.nombre_rol}' requiere un vínculo "
                    f"institucional (facultad o grupo) que este endpoint no "
                    f"gestiona. Use integracion/asignar-rol-existente/ para "
                    f"asignarlo: ese endpoint crea o actualiza el vínculo "
                    f"necesario en la misma operación."
                )

        rxu, created = RolXUsuario.objects.get_or_create(
            usuario=usuario,
            rol=rol,
            defaults={'estado': True}
        )
        auditor = ejecutor if ejecutor is not None else usuario
        if created:
            HistorialService.registrar(
                auditor,
                f"Asignó el rol '{rol.nombre_rol}' al usuario '{usuario.username}'.",
                objeto=rxu,
            )
        elif not rxu.estado:
            rxu.estado = True
            rxu.save(update_fields=['estado'])
            HistorialService.registrar(
                auditor,
                f"Reactivó el rol '{rol.nombre_rol}' (previamente retirado) "
                f"al usuario '{usuario.username}'.",
                objeto=rxu,
            )
        return rxu

    @staticmethod
    @transaction.atomic
    def borrar_rol_de_usuario(usuario_id: int, rol_id: int, ejecutor=None) -> RolXUsuario:
        rxu = get_object_or_404(
            RolXUsuario,
            usuario_id=usuario_id,
            rol_id=rol_id,
            estado=True
        )
        rxu.estado = False
        rxu.save(update_fields=['estado'])

        auditor = ejecutor if ejecutor is not None else rxu.usuario
        HistorialService.registrar(
            auditor,
            f"Removió el rol '{rxu.rol.nombre_rol}' del usuario '{rxu.usuario.username}'.",
            objeto=rxu,
        )
        return rxu

    @staticmethod
    def listar_roles_de_usuario(usuario_id: int):
        return RolXUsuario.objects.select_related('rol').filter(
            usuario_id=usuario_id,
            estado=True
        )

    @staticmethod
    def listar_roles_historico_de_usuario(usuario_id: int):
        return RolXUsuario.objects.select_related('rol').filter(
            usuario_id=usuario_id
        )