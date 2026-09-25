from django.urls import reverse
from rest_framework import status
from apps.common.models.historial import Historial
from .base import BaseUsuarioTestCase


class UsuarioXPersonaTests(BaseUsuarioTestCase):
           
    def test_historial_se_registra(self):
        new_persona_id = self.persona.id
        url = reverse('usuario-persona-reasignar')  
        data = {'usuario_id': self.usuario.id, 'persona_id': new_persona_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        historial = Historial.objects.filter(
            usuario=self.usuario,
            accion__icontains="reasigna persona"
        ).first()
        self.assertIsNotNone(historial)
