"""
Reasigna la Persona vinculada a un Usuario existente.
La CUENTA (Usuario) es permanente; lo que cambia es la PERSONA
asignada. Secuencia:
    1. Cierra las PersonaXGrupo activas de la persona anterior.
    2. Crea la nueva Persona.
    3. Reasigna la Persona al Usuario (cierra la UsuarioXPersona
        anterior y abre una nueva).
    4. Determina el rol final.
    5. Si el rol final requiere facultad o grupo (ROLES_CON_FACULTAD
        / ROLES_CON_GRUPO) y el body trae los datos necesarios,
        crea la PersonaXGrupo correspondiente para la nueva persona.
    6. Si se indicó un rol_plataforma_id distinto, reemplaza el rol.
"""
#apps/integracion/services/vinculacion_service.py
import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from apps.common.services.historial_service import HistorialService
from apps.institucional.models.persona import Persona
from apps.institucional.services.persona_service import PersonaService
from apps.institucional.services.persona_x_grupo_service import PersonaXGrupoService
from apps.integracion.selectors.vinculacion_selector import VinculacionSelector
from apps.integracion.validators.vinculacion_validator import VinculacionValidator
from apps.usuarios.models import RolPlataforma
from apps.usuarios.models.usuario_x_persona import UsuarioXPersona
from apps.usuarios.services.password_service import PasswordService
from apps.usuarios.services.rol_x_usuario_service import RolXUsuarioService
from apps.usuarios.services.interfaces import GestionUsuarioInterface
from apps.usuarios.constants import ROLES_CON_FACULTAD, ROLES_CON_GRUPO

User = get_user_model()

# --------------------------------------------------------------------- #
# Nombres de rol de plataforma.
# --------------------------------------------------------------------- #
ROL_SOPORTE = "SOPORTE"
ROL_SUPERVISOR = "SUPERVISOR"
ROL_GERENTE = "GERENTE"
ROL_DECANO = "DECANO"
ROL_FACULTAD = "FACULTAD"
ROL_ESTUDIANTE = "ESTUDIANTE"
ROL_JURADO = "JURADO"
ROL_TUTOR = "TUTOR"
ROL_GRUPO = "GRUPO"
ROL_CINTERNO = "CINTERNO"
ROL_CEXTERNO = "CEXTERNO"
ROL_ASESOR = "ASESOR"


class VinculacionService(GestionUsuarioInterface):

    # ------------------------------------------------------------------ #
    # Métodos privados de utilidad
    # ------------------------------------------------------------------ #
    @staticmethod
    def _generar_password(longitud: int = 10) -> str:
        """Genera contraseña temporal segura (mejora sobre RandomString.make(8) de Thymeleaf)."""
        alfabeto = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alfabeto) for _ in range(longitud))

    @staticmethod
    def _generar_username(correo: str) -> str:
        """Genera username a partir del correo (política institucional actual)."""
        return correo.lower().strip()

    # ------------------------------------------------------------------ #
    # Bloques privados de construcción (se combinan en los tres flujos)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _crear_persona(data: dict, ejecutor):
        return PersonaService.crear(
            grado_id=data['grado_id'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            documento=data['documento'],
            celular=data['celular'],
            correo=data['correo'],
            cvlac=data.get('cvlac'),
            ejecutor=ejecutor,
        )

    @staticmethod
    def _crear_usuario(persona, data: dict, ejecutor):
        """
        Crea Usuario + UsuarioXPersona + programa el envío del enlace de
        credenciales. El password se genera automáticamente si no viene
        en data. El username se genera a partir del correo si no viene.
        """
        password = data.get('password') or VinculacionService._generar_password()
        username = data.get('username') or VinculacionService._generar_username(persona.correo)
        return VinculacionService.crear_credenciales(
            data={
                'username': username,
                'email': persona.correo,
                'password': password,
                'is_active': True,
                'persona_fk': persona.pk,
            },
            ejecutor=ejecutor,
        )

    @staticmethod
    def _asignar_rol(usuario, rol_plataforma_id: int, ejecutor) -> None:
        RolXUsuarioService.agregar_rol_a_usuario(
            usuario_id=usuario.pk,
            rol_id=rol_plataforma_id,
            ejecutor=ejecutor,
        )

    @staticmethod
    def _crear_vinculacion_facultad(persona, rol_grupo_id: int, facultad_id: int, ejecutor):
        return PersonaXGrupoService.crear(
            persona_id=persona.pk,
            rol_grupo_id=rol_grupo_id,
            grupo_id=None,
            facultad_id=facultad_id,
            vinculacion=django_timezone.now().date(),
            ejecutor=ejecutor,
        )

    @staticmethod
    def _crear_vinculacion_grupo(persona, rol_grupo_id: int, grupo_id: int, ejecutor):
        """
        La facultad NO se pasa: PersonaXGrupoService deriva internamente la
        facultad de referencia desde FacultadXGrupo (derivar_facultad_de_grupo=True),
        porque esta persona es nueva y nunca tuvo una facultad previa.
        """
        return PersonaXGrupoService.crear(
            persona_id=persona.pk,
            rol_grupo_id=rol_grupo_id,
            grupo_id=grupo_id,
            facultad_id=None,
            vinculacion=django_timezone.now().date(),
            ejecutor=ejecutor,
            derivar_facultad_de_grupo=True,
        )
    
    @staticmethod
    def _crear_o_actualizar_vinculacion(persona, rol_grupo_id, facultad_id, grupo_id, ejecutor):
        """
        Si la Persona ya tiene una vinculación PersonaXGrupo
        activa, la actualiza (solo toca los campos que vienen no-None);
        si no tiene ninguna, crea una nueva.
        """
        vinculo_activo = PersonaXGrupoService.listar_activas_persona(persona.pk).first()
        if vinculo_activo is None:
            return PersonaXGrupoService.crear(
                persona_id=persona.pk,
                rol_grupo_id=rol_grupo_id,
                grupo_id=grupo_id,
                facultad_id=facultad_id,
                vinculacion=django_timezone.now().date(),
                ejecutor=ejecutor,
            )
        return PersonaXGrupoService.actualizar(
            vinculo_activo.pk,
            ejecutor=ejecutor,
            rol_grupo_id=rol_grupo_id,
            facultad_id=facultad_id,
            grupo_id=grupo_id,
        )

    @staticmethod
    def _registrar_historial(ejecutor, mensaje: str, objeto=None) -> None:
        HistorialService.registrar(ejecutor, mensaje, objeto=objeto)

    # ------------------------------------------------------------------ #
    # Tres flujos núcleo
    # ------------------------------------------------------------------ #
    @staticmethod
    @transaction.atomic
    def _flujo_administrativo(data: dict, ejecutor, nombre_rol: str) -> dict:
        """
        Flujo 1: Persona + Usuario + RolPlataforma + UsuarioXPersona.
        Sin PersonaXGrupo. Equivale a guardarPersonaSinGrupoNiFacultad().
        """
        VinculacionValidator.validar_datos_flujo_administrativo(data)
        persona = VinculacionService._crear_persona(data, ejecutor)
        usuario = VinculacionService._crear_usuario(persona, data, ejecutor)
        VinculacionService._asignar_rol(usuario, data['rol_plataforma_id'], ejecutor)
        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' registró el usuario "
            f"administrativo '{usuario.username}' (rol={nombre_rol}, "
            f"persona={persona.nombre} {persona.apellido}).",
            objeto=usuario,
        )
        return {'persona': persona, 'usuario': usuario}

    @staticmethod
    @transaction.atomic
    def _flujo_facultad(data: dict, ejecutor, nombre_rol: str) -> dict:
        """
        Flujo 2: + PersonaXGrupo(facultad=<X>, grupo=None).
        """
        VinculacionValidator.validar_datos_flujo_facultad(data)
        persona = VinculacionService._crear_persona(data, ejecutor)
        usuario = VinculacionService._crear_usuario(persona, data, ejecutor)
        vinculacion = VinculacionService._crear_vinculacion_facultad(
            persona, data['rol_grupo_id'], data['facultad_id'], ejecutor,
        )
        VinculacionService._asignar_rol(usuario, data['rol_plataforma_id'], ejecutor)
        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' registró '{usuario.username}' "
            f"(rol={nombre_rol}, facultad_id={data['facultad_id']}, "
            f"persona={persona.nombre} {persona.apellido}).",
            objeto=vinculacion,
        )
        return {'persona': persona, 'usuario': usuario, 'vinculacion': vinculacion}

    @staticmethod
    @transaction.atomic
    def _flujo_grupo(data: dict, ejecutor, nombre_rol: str) -> dict:
        """
        Flujo 3: + PersonaXGrupo(grupo=<X>, facultad=None).
        La facultad se deriva automáticamente de FacultadXGrupo 
        dentro de PersonaXGrupoService.
        """
        VinculacionValidator.validar_datos_flujo_grupo(data)
        persona = VinculacionService._crear_persona(data, ejecutor)
        usuario = VinculacionService._crear_usuario(persona, data, ejecutor)
        vinculacion = VinculacionService._crear_vinculacion_grupo(
            persona, data['rol_grupo_id'], data['grupo_id'], ejecutor,
        )
        VinculacionService._asignar_rol(usuario, data['rol_plataforma_id'], ejecutor)
        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' registró investigador "
            f"'{usuario.username}' (rol={nombre_rol}, grupo_id={data['grupo_id']}, "
            f"persona={persona.nombre} {persona.apellido}).",
            objeto=vinculacion,
        )
        return {'persona': persona, 'usuario': usuario, 'vinculacion': vinculacion}

    # ------------------------------------------------------------------ #
    # 12 endpoints de creación (uno por rol de plataforma)
    # ------------------------------------------------------------------ #
    @staticmethod
    def crear_usuario_soporte(data: dict, ejecutor):
        return VinculacionService._flujo_administrativo(data, ejecutor, ROL_SOPORTE)

    @staticmethod
    def crear_usuario_supervisor(data: dict, ejecutor):
        return VinculacionService._flujo_administrativo(data, ejecutor, ROL_SUPERVISOR)

    @staticmethod
    def crear_usuario_gerente(data: dict, ejecutor):
        return VinculacionService._flujo_administrativo(data, ejecutor, ROL_GERENTE)

    @staticmethod
    def crear_usuario_decano(data: dict, ejecutor):
        return VinculacionService._flujo_facultad(data, ejecutor, ROL_DECANO)

    @staticmethod
    def crear_usuario_facultad(data: dict, ejecutor):
        return VinculacionService._flujo_facultad(data, ejecutor, ROL_FACULTAD)

    @staticmethod
    def crear_usuario_estudiante(data: dict, ejecutor):
        return VinculacionService._flujo_facultad(data, ejecutor, ROL_ESTUDIANTE)

    @staticmethod
    def crear_usuario_jurado(data: dict, ejecutor):
        return VinculacionService._flujo_facultad(data, ejecutor, ROL_JURADO)

    @staticmethod
    def crear_usuario_tutor(data: dict, ejecutor):
        return VinculacionService._flujo_facultad(data, ejecutor, ROL_TUTOR)

    @staticmethod
    def crear_usuario_grupo(data: dict, ejecutor):
        return VinculacionService._flujo_grupo(data, ejecutor, ROL_GRUPO)

    @staticmethod
    def crear_usuario_cinterno(data: dict, ejecutor):
        return VinculacionService._flujo_grupo(data, ejecutor, ROL_CINTERNO)

    @staticmethod
    def crear_usuario_cexterno(data: dict, ejecutor):
        return VinculacionService._flujo_grupo(data, ejecutor, ROL_CEXTERNO)

    @staticmethod
    def crear_usuario_asesor(data: dict, ejecutor):
        return VinculacionService._flujo_grupo(data, ejecutor, ROL_ASESOR)

    # ------------------------------------------------------------------ #
    # Reemplazo: reasignar Persona al mismo Usuario
    # ------------------------------------------------------------------ #
    @staticmethod
    @transaction.atomic
    def reemplazar_usuario(usuario_id: int, data: dict, ejecutor) -> dict:
        """
        Reasigna la Persona vinculada a un Usuario existente.
        La CUENTA (Usuario) es permanente; lo que cambia es la PERSONA
        asignada. Secuencia:
          1. Cierra las PersonaXGrupo activas de la persona anterior.
          2. Crea la nueva Persona.
          3. Reasigna la Persona al Usuario (cierra la UsuarioXPersona
             anterior y abre una nueva).
          4. Si se indica un rol_plataforma_id distinto, reemplaza el rol.
          5. Si el rol final requiere facultad o grupo (ROLES_CON_FACULTAD
             / ROLES_CON_GRUPO) y el body trae los datos necesarios,
             crea la PersonaXGrupo correspondiente para la nueva persona.
        """
        VinculacionValidator.validar_reemplazo(usuario_id)
        VinculacionValidator.validar_datos_persona(data)
        usuario = get_object_or_404(User, pk=usuario_id)
        persona_anterior = VinculacionSelector.obtener_persona_usuario(usuario_id)

        # 1. Cerrar PersonaXGrupo activas de la persona anterior
        if persona_anterior:
            from apps.institucional.models import PersonaXGrupo
            PersonaXGrupo.objects.filter(
                persona=persona_anterior, estado=True
            ).update(estado=False, desvinculacion=django_timezone.now().date())
            VinculacionService._registrar_historial(
                ejecutor,
                f"[INTEGRACION] Vinculaciones de "
                f"'{persona_anterior.nombre} {persona_anterior.apellido}' "
                f"cerradas por reemplazo del usuario '{usuario.username}'.",
                objeto=persona_anterior,
            )

        # 2. Crear nueva Persona
        nueva_persona = VinculacionService._crear_persona(data, ejecutor)

        # 3. Reasignar Persona al Usuario (cierra la antigua UsuarioXPersona
        #    y crea la nueva)
        VinculacionService.reasignar_persona_a_usuario(
            usuario_id=usuario_id,
            nueva_persona_id=nueva_persona.pk,
            ejecutor=ejecutor,
        )

        # 4. Reasignar rol si se indica uno distinto
        nombre_rol_final = None
        rol_plataforma_id_nuevo = data.get('rol_plataforma_id')
        if rol_plataforma_id_nuevo:
            rol_obj = get_object_or_404(RolPlataforma, pk=rol_plataforma_id_nuevo)
            nombre_rol_final = rol_obj.nombre_rol
        else:
            rol_activo = VinculacionSelector.obtener_rol_plataforma(usuario.pk)
            nombre_rol_final = rol_activo.nombre_rol if rol_activo else None

        # 5. Crear PersonaXGrupo para la nueva persona, según el tipo de
        #    vinculación que exige el rol final.
        vinculacion = None
        if nombre_rol_final in ROLES_CON_FACULTAD and data.get('facultad_id'):
            vinculacion = VinculacionService._crear_vinculacion_facultad(
                nueva_persona, data.get('rol_grupo_id'), data['facultad_id'], ejecutor,
            )
        elif nombre_rol_final in ROLES_CON_GRUPO and data.get('grupo_id'):
            vinculacion = VinculacionService._crear_vinculacion_grupo(
                nueva_persona, data.get('rol_grupo_id'), data['grupo_id'], ejecutor,
            )
        
        # 6. Reemplazar el rol de plataforma, si se indicó uno distinto
        if rol_plataforma_id_nuevo:
            roles_activos = RolXUsuarioService.listar_roles_de_usuario(usuario.pk)
            for rol in roles_activos:
                RolXUsuarioService.borrar_rol_de_usuario(
                    usuario_id=usuario.pk,
                    rol_id=rol.rol_id,
                    ejecutor=ejecutor,
                )
            VinculacionService._asignar_rol(usuario, rol_plataforma_id_nuevo, ejecutor)

        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' reemplazó la persona del "
            f"usuario '{usuario.username}': "
            f"'{persona_anterior.nombre if persona_anterior else 'N/A'}' -> "
            f"'{nueva_persona.nombre} {nueva_persona.apellido}'.",
            objeto=usuario,
        )
        return {
            'usuario': usuario,
            'persona_anterior': persona_anterior,
            'nueva_persona': nueva_persona,
            'vinculacion': vinculacion,
        }

    # ------------------------------------------------------------------ #
    # Retiro: soft-delete completo sin eliminar nada
    # ------------------------------------------------------------------ #
    @staticmethod
    @transaction.atomic
    def retirar_usuario(usuario_id: int, ejecutor, fecha_retiro=None) -> dict:
        """
        Retira al usuario: desactiva todo sin eliminar ningún registro.
          1. Usuario.is_active=False + tokens invalidados
          2. UsuarioXPersona activa cerrada
          3. PersonaXGrupo activas -> estado=False + desvinculacion=hoy
        La Persona permanece activa (registro histórico permanente).
        """
        VinculacionValidator.validar_retiro(usuario_id)
        fecha_retiro = fecha_retiro or django_timezone.now().date()
        usuario = get_object_or_404(User, pk=usuario_id)

        # Guardar la persona ANTES de desactivar (el selector la lee por estado=True)
        persona = VinculacionSelector.obtener_persona_usuario(usuario_id)

        # 1. Desactivar Usuario + invalidar tokens
        VinculacionService.desactivar_usuario(usuario_id, ejecutor)

        # 2. Desactivar PersonaXGrupo activas
        if persona:
            vinculos = PersonaXGrupoService.listar_activas_persona(persona.pk)
            for vinculo in vinculos:
                PersonaXGrupoService.eliminar(
                    persona_x_grupo_id=vinculo.pk,
                    ejecutor=ejecutor,
                    desvinculacion=fecha_retiro,
                )

        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' retiró al usuario "
            f"'{usuario.username}' (id={usuario_id}) con fecha {fecha_retiro}. "
            f"Desactivados: Usuario, UsuarioXPersona, PersonaXGrupo.",
            objeto=usuario,
        )
        return {'usuario': usuario, 'retirado': True}
    
    @staticmethod
    @transaction.atomic
    def asignar_rol_existente(usuario_id: int, rol_plataforma_id: int, ejecutor,
                               rol_grupo_id: int = None, facultad_id: int = None,
                               grupo_id: int = None) -> dict:
        """
        Asigna un RolPlataforma a un Usuario ya existente. Si ese rol
        pertenece a ROLES_CON_FACULTAD o ROLES_CON_GRUPO, crea o actualiza
        en la MISMA transacción el PersonaXGrupo de la Persona actualmente
        asignada a ese Usuario.
        """
        rol = get_object_or_404(RolPlataforma, pk=rol_plataforma_id)
        usuario = get_object_or_404(User, pk=usuario_id)
        persona = VinculacionSelector.obtener_persona_usuario(usuario_id)
        vinculo = None
        if rol.nombre_rol in ROLES_CON_FACULTAD:
            VinculacionValidator.validar_persona_para_rol_institucional(
                usuario_id, persona, rol.nombre_rol,
            )
            VinculacionValidator.validar_datos_asignacion_rol_existente(
                {'rol_grupo_id': rol_grupo_id, 'facultad_id': facultad_id},
                requiere='facultad',
            )
            vinculo = VinculacionService._crear_o_actualizar_vinculacion(
                persona, rol_grupo_id, facultad_id, None, ejecutor,
            )
        elif rol.nombre_rol in ROLES_CON_GRUPO:
            VinculacionValidator.validar_persona_para_rol_institucional(
                usuario_id, persona, rol.nombre_rol,
            )
            VinculacionValidator.validar_datos_asignacion_rol_existente(
                {'rol_grupo_id': rol_grupo_id, 'grupo_id': grupo_id},
                requiere='grupo',
            )
            vinculo = VinculacionService._crear_o_actualizar_vinculacion(
                persona, rol_grupo_id, None, grupo_id, ejecutor,
            )
        RolXUsuarioService.agregar_rol_a_usuario(
            usuario_id=usuario.pk, rol_id=rol_plataforma_id, ejecutor=ejecutor,
        )
        VinculacionService._registrar_historial(
            ejecutor,
            f"[INTEGRACION] '{ejecutor.username}' asignó el rol "
            f"'{rol.nombre_rol}' al usuario '{usuario.username}'" + (
                f" y vinculó a '{persona.nombre} {persona.apellido}' "
                f"({'facultad_id=' + str(facultad_id) if facultad_id else 'grupo_id=' + str(grupo_id)})."
                if vinculo else "."
            ),
            objeto=usuario,
        )
        return {'usuario': usuario, 'rol': rol, 'vinculacion': vinculo}

    # ------------------------------------------------------------------ #
    # Implementación concreta de GestionUsuarioInterface.
    # Aquí SÍ es correcto importar de apps.usuarios (modelos, no vistas):
    # integración se apoya en usuarios, conforme a 01_architecture.md.
    # ------------------------------------------------------------------ #
    @staticmethod
    @transaction.atomic
    def crear_credenciales(data: dict, ejecutor) -> User:
        password_temporal = data['password']
        validate_password(password_temporal)
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=password_temporal,
            is_active=data.get('is_active', True),
        )
        user.debe_cambiar_password = True
        # Genera el token de establecimiento inicial, reutilizando el mismo
        # campo que usa la recuperación de contraseña (token_recuperacion).
        token = secrets.token_urlsafe(32)
        user.token_recuperacion = token
        user.token_creado_en = django_timezone.now()
        # Registra quién creó la cuenta (ej. Facultad), para poder
        # scoparle la gestión (desactivar/activar/listar) más adelante.
        if ejecutor is not None and getattr(ejecutor, 'is_authenticated', False):
            user.creado_por = ejecutor
        user.save(update_fields=[
            'debe_cambiar_password', 'token_recuperacion', 'token_creado_en', 'creado_por',
        ])
        user.save(update_fields=['debe_cambiar_password', 'token_recuperacion', 'token_creado_en'])
        persona_id = data.get('persona_fk')
        if persona_id:
            try:
                persona = Persona.objects.get(pk=persona_id)
                UsuarioXPersona.objects.create(usuario=user, persona=persona, estado=True)
            except Persona.DoesNotExist:
                pass
        VinculacionService._enviar_enlace_establecimiento_password(
            email=user.email, username=user.username, token=token
        )
        HistorialService.registrar(
            ejecutor,
            f"Se crearon las credenciales del usuario '{user.username}' y se envió un enlace "
            "para establecer su contraseña inicial (sin transmitir la contraseña por correo).",
        )
        return user
    
    @staticmethod
    def _ejecutor_es_soporte(ejecutor) -> bool:
        from apps.usuarios.models import RolXUsuario
        return RolXUsuario.objects.filter(
            usuario=ejecutor, rol__nombre_rol=ROL_SOPORTE, estado=True,
        ).exists()

    @staticmethod
    def _ejecutor_es_facultad(ejecutor) -> bool:
        from apps.usuarios.models import RolXUsuario
        return RolXUsuario.objects.filter(
            usuario=ejecutor, rol__nombre_rol=ROL_FACULTAD, estado=True,
        ).exists()

    @staticmethod
    def _validar_puede_gestionar_usuario(usuario_objetivo, ejecutor):
        """Soporte puede desactivar/activar cualquier usuario. Facultad solo
        puede hacerlo sobre usuarios que ella misma creó (creado_por)."""
        from rest_framework.exceptions import PermissionDenied
        if VinculacionService._ejecutor_es_soporte(ejecutor):
            return
        if (VinculacionService._ejecutor_es_facultad(ejecutor)
                and usuario_objetivo.creado_por_id == ejecutor.id):
            return
        raise PermissionDenied(
            "Solo puedes gestionar usuarios que tú mismo creaste."
        )

    @staticmethod
    def desactivar_usuario(user_id: int, ejecutor, forzar=False):
        """Desactiva un usuario (Soft Delete) estableciendo is_active = False."""
        user = get_object_or_404(User, pk=user_id)
        if not forzar:
            VinculacionService._validar_puede_gestionar_usuario(user, ejecutor)
        user.is_active = False
        user.save(update_fields=['is_active'])
        tokens_activos = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
        for token in tokens_activos:
            BlacklistedToken.objects.get_or_create(token=token)
        HistorialService.registrar(
            ejecutor, f"Se desactivó el usuario {user.username} e invalidaron sus sesiones activas."
        )
        return user

    @staticmethod
    def activar_usuario(user_id: int, ejecutor):
        """Activa un usuario estableciendo is_active = True."""
        user = get_object_or_404(User, pk=user_id)
        VinculacionService._validar_puede_gestionar_usuario(user, ejecutor)
        user.is_active = True
        user.save(update_fields=['is_active'])
        HistorialService.registrar(ejecutor, f"Se activó el usuario {user.username}. Debe iniciar sesión nuevamente.")
        return user

    @staticmethod
    def listar_creados_por(ejecutor):
        return User.objects.filter(creado_por=ejecutor).order_by('-date_joined')

    @staticmethod
    def reactivar_usuario(user_id: int, ejecutor):
        return VinculacionService.activar_usuario(user_id, ejecutor)

    @staticmethod
    @transaction.atomic
    def reasignar_persona_a_usuario(usuario_id: int, nueva_persona_id: int, ejecutor) -> UsuarioXPersona:
        """
        Cierra la asignación activa actual (si existe) y crea una nueva.
        Nunca hay dos asignaciones activas simultáneas para el mismo usuario
        (constraint 'unique_active_assignment_per_user').
        """
        usuario = get_object_or_404(User, pk=usuario_id)
        nueva_persona = get_object_or_404(Persona, pk=nueva_persona_id)
        asignacion_actual = UsuarioXPersona.objects.select_for_update().filter(
            usuario=usuario, estado=True
        ).first()
        if asignacion_actual:
            if asignacion_actual.persona_id == nueva_persona.id:
                # Ya está asignada a esa misma persona: no-op idempotente,
                # evita cerrar y reabrir una asignación idéntica, pero se
                # deja constancia en el historial del intento.
                HistorialService.registrar(
                    ejecutor,
                    f"Reasigna persona '{nueva_persona.nombre} {nueva_persona.apellido}' "
                    f"al usuario '{usuario.username}' (ya estaba asignada; no se realizó cambio).",
                    objeto=asignacion_actual,
                )
                return asignacion_actual
            asignacion_actual.estado = False
            asignacion_actual.fecha_fin = django_timezone.now()
            asignacion_actual.save(update_fields=['estado', 'fecha_fin'])
        nueva_asignacion = UsuarioXPersona.objects.create(
            usuario=usuario,
            persona=nueva_persona,
            estado=True
        )
        HistorialService.registrar(
            ejecutor,
            f"Reasigna persona '{nueva_persona.nombre} {nueva_persona.apellido}' "
            f"al usuario '{usuario.username}'"
            + (f", reemplazando a '{asignacion_actual.persona.nombre} {asignacion_actual.persona.apellido}'."
               if asignacion_actual else "."),
            objeto=nueva_asignacion,
        )
        return nueva_asignacion

    @staticmethod
    def _enviar_enlace_establecimiento_password(email: str, username: str, token: str):
        """
        Reemplaza el envío de contraseña en texto plano: se envía un enlace
        de un solo uso hacia el flujo de reset-password ya existente.
        """
        if not email:
            return

        from django.conf import settings
        from apps.common.services.email_service import EmailService

        link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Confirmación de datos de acceso"
        message = (
            "Gusto en saludarlo,\n\n"
            f"Su usuario '{username}' para la plataforma se creó de forma exitosa.\n"
            "Por seguridad, no enviamos su contraseña por correo. Haga click en el "
            f"siguiente enlace para establecer su contraseña de acceso:\n\n{link}\n\n"
            f"El enlace expirará en {PasswordService.TOKEN_EXPIRATION_HOURS} hora(s).\n\n"
            "Bienvenido a la plataforma ROSILLO."
        )
        EmailService.enviar(subject=subject, message=message, recipient_list=[email])