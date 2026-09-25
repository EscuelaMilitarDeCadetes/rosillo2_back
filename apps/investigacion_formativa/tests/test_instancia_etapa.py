from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.instancia_etapa_service import InstanciaEtapaService


class InstanciaEtapaServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_instancia(self):
        # self.instancia_etapa (fixture base) ya ocupa proceso+etapa_origen,
        # así que estas pruebas usan etapa_destino para no chocar con unique_together.
        return InstanciaEtapaService.crear(
            proceso_id=self.proceso.pk,
            etapa_id=self.etapa_destino.pk,
            ejecutor=self.ejecutor,
        )

    def test_crear_instancia_exitosa(self):
        instancia = self._crear_instancia()
        self.assertEqual(instancia.estado, 'PENDIENTE')

    def test_crear_instancia_duplicada_para_misma_etapa_falla(self):
        self._crear_instancia()
        with self.assertRaises(ValidationError):
            InstanciaEtapaService.crear(
                proceso_id=self.proceso.pk, etapa_id=self.etapa_destino.pk, ejecutor=self.ejecutor,
            )

    def test_iniciar_instancia_exitoso(self):
        instancia = self._crear_instancia()
        iniciada = InstanciaEtapaService.iniciar(instancia.pk, ejecutor=self.ejecutor)
        self.assertEqual(iniciada.estado, 'EN_PROCESO')
        self.assertIsNotNone(iniciada.fecha_inicio)

    def test_aprobar_instancia_sin_iniciar_falla(self):
        instancia = self._crear_instancia()
        with self.assertRaises(ValidationError):
            InstanciaEtapaService.aprobar(instancia.pk, ejecutor=self.ejecutor)

    def test_aprobar_instancia_exitoso(self):
        instancia = self._crear_instancia()
        InstanciaEtapaService.iniciar(instancia.pk, ejecutor=self.ejecutor)
        aprobada = InstanciaEtapaService.aprobar(instancia.pk, ejecutor=self.ejecutor)
        self.assertEqual(aprobada.estado, 'APROBADO')
        self.assertIsNotNone(aprobada.fecha_fin)

    def test_rechazar_instancia_exitoso(self):
        instancia = self._crear_instancia()
        InstanciaEtapaService.iniciar(instancia.pk, ejecutor=self.ejecutor)
        rechazada = InstanciaEtapaService.rechazar(instancia.pk, ejecutor=self.ejecutor)
        self.assertEqual(rechazada.estado, 'RECHAZADO')

    def test_marcar_segunda_instancia_exitoso(self):
        instancia = self._crear_instancia()
        InstanciaEtapaService.iniciar(instancia.pk, ejecutor=self.ejecutor)
        InstanciaEtapaService.rechazar(instancia.pk, ejecutor=self.ejecutor)
        con_segunda = InstanciaEtapaService.marcar_segunda_instancia(instancia.pk, ejecutor=self.ejecutor)
        self.assertEqual(con_segunda.estado, 'SEGUNDA_INSTANCIA')

    def test_listar_por_proceso_incluye_la_de_la_fixture_base(self):
        self._crear_instancia()
        resultado = InstanciaEtapaService.listar_por_proceso(self.proceso.pk)
        # self.instancia_etapa (fixture base, etapa_origen) + la nueva (etapa_destino)
        self.assertEqual(resultado.count(), 2)
        
    def test_iniciar_instancia_con_ejecutor_sin_rol_responsable_falla(self):
        from rest_framework.exceptions import PermissionDenied
        from apps.usuarios.models import Usuario
        ajeno = Usuario.objects.create_user(
            username='ajeno@esmic.edu.co', email='ajeno@esmic.edu.co', password='ajeno123',
        )  # sin RolXUsuario ni ParticipanteProceso
        instancia = self._crear_instancia()
        with self.assertRaises(PermissionDenied):
            InstanciaEtapaService.iniciar(instancia.pk, ejecutor=ajeno)