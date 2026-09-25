# apps/investigacion_formal/tests/test_investigador_completo_service.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.institucional.models import PersonaXGrupo
from apps.investigacion_formal.models import InvestigadorXProyecto
from apps.investigacion_formal.services.investigador_completo_service import (
    InvestigadorCompletoService,
)
from .base import InvestigacionFormalFixturesMixin


class InvestigadorCompletoServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.rol_investigador = self._crear_rol_investigador()

    def _datos_base(self, documento='NUEVO-001', correo='nuevo@esmic.edu.co',
                     celular='3009999999'):
        return dict(
            grado_id=self.grado.pk,
            nombre='Nuevo',
            apellido='Investigador',
            documento=documento,
            celular=celular,
            correo=correo,
            grupo_id=self.grupo.pk,
            rol_grupo_id=self.rol_grupo.pk,
            proyecto_id=self.proyecto.pk,
            rol_investigador_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
        )

    def test_registrar_completo_exitoso_crea_las_tres_filas(self):
        investigador = InvestigadorCompletoService.registrar_completo(
            **self._datos_base()
        )
        self.assertIsInstance(investigador, InvestigadorXProyecto)
        self.assertTrue(investigador.estado)
        self.assertEqual(investigador.proyecto_id, self.proyecto.pk)
        self.assertEqual(investigador.rol_investigador_id, self.rol_investigador.pk)

        persona_x_grupo = investigador.persona_x_grupo
        self.assertEqual(persona_x_grupo.grupo_id, self.grupo.pk)
        self.assertEqual(persona_x_grupo.rol_grupo_id, self.rol_grupo.pk)
        self.assertTrue(persona_x_grupo.estado)

        persona = persona_x_grupo.persona
        self.assertEqual(persona.documento, 'NUEVO-001')
        self.assertEqual(persona.correo, 'nuevo@esmic.edu.co')

    def test_registrar_completo_deriva_facultad_del_grupo(self):
        # self.facultad <-> self.grupo ya están vinculados por FacultadXGrupo
        # en el setUp del fixture mixin (ver base.py). La facultad derivada
        # se usa SOLO para validar la correspondencia grupo-facultad (ver
        # PersonaXGrupoValidator._validar_correspondencia_grupo_facultad);
        # no se persiste, porque esta Persona es nueva y nunca tuvo una
        # facultad propia -- mismo comportamiento que
        # VinculacionService._crear_vinculacion_grupo. Si la derivación
        # fallara (grupo no correspondiente a ninguna facultad), esta
        # llamada habría lanzado ValidationError.
        investigador = InvestigadorCompletoService.registrar_completo(
            **self._datos_base()
        )
        self.assertIsNone(investigador.persona_x_grupo.facultad_id)
        self.assertEqual(investigador.persona_x_grupo.grupo_id, self.grupo.pk)

    def test_registrar_completo_documento_duplicado_falla_y_no_deja_huerfanos(self):
        InvestigadorCompletoService.registrar_completo(**self._datos_base())
        conteo_personas_antes = PersonaXGrupo.objects.count()

        with self.assertRaises(ValidationError):
            InvestigadorCompletoService.registrar_completo(
                **self._datos_base(correo='otro@esmic.edu.co', celular='3008888888')
                # mismo documento='NUEVO-001' -> Persona.documento es unique
            )

        # La transacción atómica debe haber revertido TODO: ni la Persona
        # duplicada ni su PersonaXGrupo deben haber quedado creados.
        self.assertEqual(PersonaXGrupo.objects.count(), conteo_personas_antes)

    def test_registrar_completo_sin_rol_grupo_falla(self):
        # rol_grupo_id es obligatorio incondicionalmente en
        # PersonaXGrupoValidator._validar_rol_grupo_existe, a diferencia de
        # grupo_id (que sí puede ser None para una PersonaXGrupo puramente
        # administrativa) — este es el campo que garantiza fallo aquí.
        datos = self._datos_base()
        datos['rol_grupo_id'] = None
        with self.assertRaises(ValidationError):
            InvestigadorCompletoService.registrar_completo(**datos)

    def test_registrar_completo_sin_rol_investigador_falla(self):
        datos = self._datos_base()
        datos['rol_investigador_id'] = None
        with self.assertRaises(ValidationError):
            InvestigadorCompletoService.registrar_completo(**datos)

    def test_registrar_completo_dos_investigadores_distintos_en_mismo_proyecto(self):
        # Cada llamada crea SIEMPRE una Persona nueva (a diferencia de
        # AddInvestigadorProyectoModal/InvestigadorXProyectoService.crear(),
        # que reutiliza una PersonaXGrupo ya existente). La reincorporación
        # de un investigador retirado no aplica a este orquestador porque
        # nunca reutiliza una Persona/PersonaXGrupo preexistente — ese caso
        # ya está cubierto en InvestigadorXProyectoServiceTests.
        primero = InvestigadorCompletoService.registrar_completo(
            **self._datos_base(documento='NUEVO-001', correo='uno@esmic.edu.co', celular='3001111111')
        )
        segundo = InvestigadorCompletoService.registrar_completo(
            **self._datos_base(documento='NUEVO-002', correo='dos@esmic.edu.co', celular='3002222222')
        )
        self.assertNotEqual(
            primero.persona_x_grupo_id, segundo.persona_x_grupo_id
        )
        self.assertEqual(
            InvestigadorXProyecto.objects.filter(proyecto=self.proyecto).count(), 2
        )