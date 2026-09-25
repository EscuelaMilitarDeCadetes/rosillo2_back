from apps.crm.tests.factories import ProyectoFactory
from apps.usuarios.models import Usuario


class CrmFixturesMixin:
    """
    Mixin común para los tests de crm. Provee un ejecutor (Usuario) y un
    helper para crear un Proyecto mínimo de investigacion_formal, dado que
    IndicadorImpacto e Interaccion dependen de ese modelo vía FK real.
    """

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        super().setUp()

    def _crear_proyecto(self, titulo="Proyecto prueba"):
        return ProyectoFactory.create(titulo=titulo)