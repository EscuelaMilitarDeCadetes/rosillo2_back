from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.usuarios.models import RolXUsuario
from apps.usuarios.services.usuario_service import UsuarioService


class MeView(APIView):
    """
    Devuelve los datos del usuario autenticado, sus roles activos y
    (si tiene una Persona vinculada con PersonaXGrupo activo) su
    facultad_id/grupo_id — necesarios para pantallas de autoservicio
    institucional como calificarProyectosXFacultad/XGrupo, que necesitan
    saber "mi facultad" / "mi grupo" sin exponer el resto de PersonaXGrupo.

    NOTA arquitectónica: apps.usuarios es la capa base de la que dependen
    institucional/investigacion_formal (permissions, etc.), nunca al
    revés. Este import de apps.institucional.models.PersonaXGrupo dentro
    del método (no a nivel de módulo) invierte esa dependencia solo para
    este caso puntual, evitando problemas de import circular a nivel de
    carga de módulos. Si en el futuro esto crece, considerar mover
    MeView a un endpoint compuesto en una capa superior en vez de seguir
    acumulando imports tardíos aquí.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = (
            RolXUsuario.objects
            .select_related('rol')
            .filter(usuario=request.user, estado=True)
            .values_list('rol__nombre_rol', flat=True)
        )

        facultad_id = None
        grupo_id = None
        persona_id = None                      
        persona = UsuarioService.obtener_persona_actual(request.user)
        if persona is not None:
            persona_id = persona.id            
            from apps.institucional.models import PersonaXGrupo
            vinculo = (
                PersonaXGrupo.objects
                .filter(persona=persona, estado=True)
                .first()
            )
            if vinculo is not None:
                facultad_id = vinculo.facultad_id
                grupo_id = vinculo.grupo_id

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "debe_cambiar_password": request.user.debe_cambiar_password,
            "roles": list(roles),
            "facultad_id": facultad_id,
            "grupo_id": grupo_id,
            "persona_id": persona_id,          
        })