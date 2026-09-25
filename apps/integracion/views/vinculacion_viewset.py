"""
VinculacionViewSet.
Permisos aplicados directamente en cada acción (no a nivel de clase)
para soportar las dos reglas distintas:
  - SOPORTE puede ejecutar: crear_soporte, crear_decano, crear_facultad,
    crear_grupo, crear_cinterno, crear_cexterno, crear_asesor,
    crear_supervisor, crear_gerente, reemplazar, retirar.
  - FACULTAD puede ejecutar: crear_estudiante, crear_jurado, crear_tutor,
    retirar. Las tres primeras además exigen TieneAmbitoFormativa (el
    token debe tener ambito='formativa'), ya que son operaciones propias
    de investigación formativa.
  - Las otras acciones que realiza SOPORTE exige TieneAmbitoFormal, 
    ya que son operaciones propias de investigación formal.

IMPORTANTE: cada @action debe declarar su propio permission_classes.
Esta clase NO define permission_classes ni get_permissions() a nivel de
clase, así que cualquier acción que se agregue sin ese kwarg cae al
default global (IsAuthenticated).
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.usuarios.permissions import EsSoporte, EsFacultad, TieneAmbitoFormativa, TieneAmbitoFormal
from apps.integracion.services.vinculacion_service import VinculacionService


class VinculacionViewSet(viewsets.ViewSet):
    """
    Endpoints de creación de usuarios con su vinculación institucional
    completa. Cada acción corresponde a un tipo de usuario.

    Rutas generadas por el router:
      POST /api/integracion/crear-soporte/
      POST /api/integracion/crear-decano/
      POST /api/integracion/crear-facultad/
      POST /api/integracion/crear-grupo/
      POST /api/integracion/crear-cinterno/
      POST /api/integracion/crear-cexterno/
      POST /api/integracion/crear-asesor/
      POST /api/integracion/crear-supervisor/
      POST /api/integracion/crear-gerente/
      POST /api/integracion/crear-estudiante/
      POST /api/integracion/crear-jurado/
      POST /api/integracion/crear-tutor/
      POST /api/integracion/reemplazar/
      POST /api/integracion/retirar/
    """

    # -- SOPORTE: flujo administrativo ---------------------------------- #
    @action(detail=False, methods=['post'], url_path='crear-soporte',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_soporte(self, request):
        resultado = VinculacionService.crear_usuario_soporte(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-supervisor',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_supervisor(self, request):
        resultado = VinculacionService.crear_usuario_supervisor(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-gerente',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_gerente(self, request):
        resultado = VinculacionService.crear_usuario_gerente(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    # -- SOPORTE: flujo facultad ---------------------------------------- #
    @action(detail=False, methods=['post'], url_path='crear-decano',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_decano(self, request):
        resultado = VinculacionService.crear_usuario_decano(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-facultad',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_facultad(self, request):
        resultado = VinculacionService.crear_usuario_facultad(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    # -- SOPORTE: flujo grupo ------------------------------------------- #
    @action(detail=False, methods=['post'], url_path='crear-grupo',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_grupo(self, request):
        resultado = VinculacionService.crear_usuario_grupo(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-cinterno',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_cinterno(self, request):
        resultado = VinculacionService.crear_usuario_cinterno(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-cexterno',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_cexterno(self, request):
        resultado = VinculacionService.crear_usuario_cexterno(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-asesor',
            permission_classes=[EsSoporte, TieneAmbitoFormal])
    def crear_asesor(self, request):
        resultado = VinculacionService.crear_usuario_asesor(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    # -- FACULTAD: flujo facultad (sub-roles que gestiona la facultad) -- #
    @action(detail=False, methods=['post'], url_path='crear-estudiante',
            permission_classes=[EsFacultad, TieneAmbitoFormativa])
    def crear_estudiante(self, request):
        resultado = VinculacionService.crear_usuario_estudiante(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-jurado',
            permission_classes=[EsFacultad, TieneAmbitoFormativa])
    def crear_jurado(self, request):
        resultado = VinculacionService.crear_usuario_jurado(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='crear-tutor',
            permission_classes=[EsFacultad, TieneAmbitoFormativa])
    def crear_tutor(self, request):
        resultado = VinculacionService.crear_usuario_tutor(
            data=request.data, ejecutor=request.user
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_201_CREATED)

    # -- Operaciones de ciclo de vida ----------------------------------- #
    @action(detail=False, methods=['post'], url_path='reemplazar',
            permission_classes=[EsSoporte])
    def reemplazar(self, request):
        """
        Reasigna la Persona vinculada a un Usuario existente.
        Requiere 'usuario_id' en el body + los datos de la nueva Persona.

        Operación crítica: cambia qué persona real está detrás de una
        cuenta ya existente (incluidas cuentas SOPORTE/DECANO/etc.), por
        eso queda restringida a SOPORTE únicamente, igual que crear-*.
        """
        usuario_id = request.data.get('usuario_id')
        if not usuario_id:
            return Response(
                {'error': "El campo 'usuario_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )
        resultado = VinculacionService.reemplazar_usuario(
            usuario_id=int(usuario_id),
            data=request.data,
            ejecutor=request.user,
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='retirar',
            permission_classes=[EsSoporte | EsFacultad])
    def retirar(self, request):
        """
        Retira a un usuario (soft-delete): desactiva Usuario,
        UsuarioXPersona y PersonaXGrupo sin eliminar ningún registro.
        Requiere 'usuario_id' en el body.
        """
        usuario_id = request.data.get('usuario_id')
        if not usuario_id:
            return Response(
                {'error': "El campo 'usuario_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )
        resultado = VinculacionService.retirar_usuario(
            usuario_id=int(usuario_id),
            ejecutor=request.user,
            fecha_retiro=request.data.get('fecha_retiro'),
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='asignar-rol-existente',
            permission_classes=[EsSoporte])
    def asignar_rol_existente(self, request):
        """
        Asigna un rol de plataforma a un usuario ya existente. Si el rol
        requiere vínculo institucional (facultad o grupo), crea o
        actualiza el PersonaXGrupo correspondiente en la misma operación.

        Requiere 'usuario_id' y 'rol_plataforma_id'. Según el rol:
          - ROLES_CON_FACULTAD: requiere además 'facultad_id' y 'rol_grupo_id'.
          - ROLES_CON_GRUPO: requiere además 'grupo_id' y 'rol_grupo_id'.
          - Cualquier otro rol: solo asigna el RolXUsuario.
        """
        usuario_id = request.data.get('usuario_id')
        rol_plataforma_id = request.data.get('rol_plataforma_id')
        if not usuario_id or not rol_plataforma_id:
            return Response(
                {'error': "Los campos 'usuario_id' y 'rol_plataforma_id' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )
        resultado = VinculacionService.asignar_rol_existente(
            usuario_id=int(usuario_id),
            rol_plataforma_id=int(rol_plataforma_id),
            ejecutor=request.user,
            rol_grupo_id=_to_int_or_none(request.data.get('rol_grupo_id')),
            facultad_id=_to_int_or_none(request.data.get('facultad_id')),
            grupo_id=_to_int_or_none(request.data.get('grupo_id')),
        )
        return Response(_serializar_resultado(resultado), status=status.HTTP_200_OK)


# ── Utilidad de serialización ─────────────────────────────────────────── #
def _serializar_resultado(resultado: dict) -> dict:
    """
    Convierte el dict que devuelven los flujos a algo serializable por JSON.
    Los objetos Django Model no son JSON-serializables directamente.
    Solo se exponen los IDs y nombres clave; el frontend puede hacer
    GET adicionales si necesita el objeto completo.
    """
    out = {}
    if 'persona' in resultado and resultado['persona']:
        p = resultado['persona']
        out['persona'] = {
            'id': p.pk,
            'nombre': p.nombre,
            'apellido': p.apellido,
            'documento': p.documento,
            'correo': p.correo,
        }
    if 'nueva_persona' in resultado and resultado['nueva_persona']:
        p = resultado['nueva_persona']
        out['nueva_persona'] = {
            'id': p.pk,
            'nombre': p.nombre,
            'apellido': p.apellido,
        }
    if 'usuario' in resultado and resultado['usuario']:
        u = resultado['usuario']
        out['usuario'] = {
            'id': u.pk,
            'username': u.username,
            'email': u.email,
            'is_active': u.is_active,
        }
    if 'vinculacion' in resultado and resultado['vinculacion']:
        v = resultado['vinculacion']
        out['vinculacion'] = {
            'id': v.pk,
            'facultad_id': v.facultad_id,
            'grupo_id': v.grupo_id,
            'rol_grupo_id': v.rol_grupo_id,
            'estado': v.estado,
        }
    if 'rol' in resultado and resultado['rol']:
        r = resultado['rol']
        out['rol'] = {'id': r.pk, 'nombre_rol': r.nombre_rol}
    if 'retirado' in resultado:
        out['retirado'] = resultado['retirado']
    return out

def _to_int_or_none(valor):
    """
    Normaliza a int o None antes de que
    llegue al service, para que los campos opcionales de facultad/grupo/
    rol_grupo no se guarden como string en los modelos.
    """
    if valor in (None, ''):
        return None
    return int(valor)