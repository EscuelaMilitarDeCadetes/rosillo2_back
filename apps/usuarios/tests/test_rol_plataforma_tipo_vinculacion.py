from django.test import TestCase
from apps.usuarios.models import RolPlataforma
from apps.usuarios.serializers.rol_plataforma_serializer import RolPlataformaSerializer


class RolPlataformaTipoVinculacionTests(TestCase):
    def test_rol_con_facultad(self):
        rol = RolPlataforma.objects.create(nombre_rol='DECANO', descripcion='x')
        data = RolPlataformaSerializer(rol).data
        self.assertEqual(data['tipo_vinculacion'], 'facultad')
        self.assertTrue(data['requiere_vinculacion'])

    def test_rol_con_grupo(self):
        rol = RolPlataforma.objects.create(nombre_rol='CINTERNO', descripcion='x')
        data = RolPlataformaSerializer(rol).data
        self.assertEqual(data['tipo_vinculacion'], 'grupo')

    def test_rol_sin_vinculacion(self):
        rol = RolPlataforma.objects.create(nombre_rol='SOPORTE', descripcion='x')
        data = RolPlataformaSerializer(rol).data
        self.assertIsNone(data['tipo_vinculacion'])
        self.assertFalse(data['requiere_vinculacion'])