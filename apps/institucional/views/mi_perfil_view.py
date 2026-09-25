from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from apps.usuarios.services.usuario_service import UsuarioService
from apps.institucional.serializers import PersonaSerializer
from apps.institucional.services.persona_service import PersonaService


class MiPerfilView(APIView):
    """
    Permite a cualquier usuario autenticado consultar y editar los datos
    de la Persona actualmente vinculada a su cuenta.

    Migrado desde: perfil.html (Thymeleaf, solo lectura).

    Por qué existe: PersonaViewSet (personas/) exige EsSoporte para
    update, y list/retrieve exigen roles institucionales que un usuario
    normal (ej. un estudiante) no tiene, así que nadie podía ver ni
    editar sus propios datos por esa vía. Igual que MeView resuelve
    "quién soy" a partir del propio request.user, aquí se resuelve la
    Persona asociada con UsuarioService.obtener_persona_actual(): nadie
    puede consultar ni modificar los datos de otra persona por este
    endpoint.

    documento y correo (correo institucional) NUNCA se editan aquí,
    aunque el cliente los envíe en el payload: se ignoran a propósito y
    se pasan como None a PersonaService.actualizar(), que ya interpreta
    None como "no cambiar este campo".
    """
    permission_classes = [IsAuthenticated]

    def _obtener_persona(self, request):
        persona = UsuarioService.obtener_persona_actual(request.user)
        if persona is None:
            raise NotFound("Tu usuario no tiene una persona asociada.")
        return persona

    def get(self, request):
        persona = self._obtener_persona(request)
        return Response(PersonaSerializer(persona).data)

    def patch(self, request):
        persona = self._obtener_persona(request)
        persona = PersonaService.actualizar(
            persona_id=persona.id,
            ejecutor=request.user,
            grado_id=request.data.get("grado"),
            nombre=request.data.get("nombre"),
            apellido=request.data.get("apellido"),
            celular=request.data.get("celular"),
            cvlac=request.data.get("cvlac"),
            # Nunca se exponen a edición del propio usuario:
            documento=None,
            correo=None,
        )
        return Response(PersonaSerializer(persona).data)