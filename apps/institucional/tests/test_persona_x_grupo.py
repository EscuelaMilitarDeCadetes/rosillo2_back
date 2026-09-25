from datetime import date

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.models import (
    GradoEstudios, Persona, GrupoInvestigacion, FacultadEscuela,
    FacultadXGrupo, RolGrupo,
)
from apps.institucional.services.persona_x_grupo_service import PersonaXGrupoService


class PersonaXGrupoServiceTests(TestCase):
    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.persona = Persona.objects.create(
            grado=grado, nombre='Juan', apellido='Pérez',
            documento='123456789', celular='3001234567',
            correo='juan@esmic.edu.co',
        )
        self.rol_investigador = RolGrupo.objects.create(cargo='Investigador')
        self.rol_tutor = RolGrupo.objects.create(cargo='Tutor')

        self.grupo_a = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo A', sigla_grupo='GA'
        )
        self.grupo_b = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo B', sigla_grupo='GB'
        )
        self.facultad_a = FacultadEscuela.objects.create(
            nombre_facultad='Facultad A', abreviatura='FA'
        )
        self.facultad_b = FacultadEscuela.objects.create(
            nombre_facultad='Facultad B', abreviatura='FB'
        )
        # Correspondencia grupo-facultad requerida por el validador
        FacultadXGrupo.objects.create(grupo=self.grupo_a, facultad=self.facultad_a)
        FacultadXGrupo.objects.create(grupo=self.grupo_b, facultad=self.facultad_b)

    # ---------- crear / actualizar ----------

    def test_crear_vinculacion_facultad_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        self.assertEqual(vinculo.facultad, self.facultad_a)
        self.assertIsNone(vinculo.grupo)
        self.assertTrue(vinculo.estado)

    def test_crear_vinculacion_grupo_sin_facultad_previa_falla(self):
        # Regla: para vincularse a un grupo, la persona debe tener
        # primero una facultad activa (o pasarla explícitamente y que
        # corresponda al grupo).
        with self.assertRaises(ValidationError):
            PersonaXGrupoService.crear(
                persona_id=self.persona.pk,
                rol_grupo_id=self.rol_investigador.pk,
                ejecutor=self.ejecutor,
                grupo_id=self.grupo_a.pk,
                vinculacion=date(2024, 1, 1),
            )

    def test_crear_vinculacion_grupo_con_facultad_correspondiente_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        self.assertEqual(vinculo.grupo, self.grupo_a)

    def test_crear_vinculacion_grupo_facultad_no_correspondiente_falla(self):
        with self.assertRaises(ValidationError):
            PersonaXGrupoService.crear(
                persona_id=self.persona.pk,
                rol_grupo_id=self.rol_investigador.pk,
                ejecutor=self.ejecutor,
                grupo_id=self.grupo_a.pk,
                facultad_id=self.facultad_b.pk,  # no corresponde a grupo_a
                vinculacion=date(2024, 1, 1),
            )

    def test_crear_vinculacion_duplicada_exacta_falla(self):
        PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValidationError):
            PersonaXGrupoService.crear(
                persona_id=self.persona.pk,
                rol_grupo_id=self.rol_tutor.pk,
                ejecutor=self.ejecutor,
                facultad_id=self.facultad_a.pk,
                vinculacion=date(2024, 1, 1),
            )

    def test_actualizar_vinculacion_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        actualizado = PersonaXGrupoService.actualizar(
            persona_x_grupo_id=vinculo.pk,
            ejecutor=self.ejecutor,
            rol_grupo_id=self.rol_investigador.pk,
        )
        self.assertEqual(actualizado.rol_grupo, self.rol_investigador)

    # ---------- trasladar_a_grupo ----------

    def test_trasladar_a_grupo_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )

        # Damos correspondencia también para grupo_b/facultad_b (ya existe en setUp)
        # y actualizamos la facultad del vínculo antes de trasladar, ya que
        # el validador de traslado exige correspondencia con la facultad
        # actualmente registrada en el vínculo.
        vinculo.facultad_id = self.facultad_b.pk
        vinculo.save(update_fields=["facultad"])

        trasladado = PersonaXGrupoService.trasladar_a_grupo(
            persona_x_grupo_id=vinculo.pk,
            nuevo_grupo_id=self.grupo_b.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(trasladado.grupo, self.grupo_b)

    def test_trasladar_a_grupo_vinculacion_de_facultad_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,  # es de facultad, no de grupo
            vinculacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValueError):
            PersonaXGrupoService.trasladar_a_grupo(
                persona_x_grupo_id=vinculo.pk,
                nuevo_grupo_id=self.grupo_b.pk,
                ejecutor=self.ejecutor,
            )

    def test_trasladar_a_grupo_inexistente_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValueError):
            PersonaXGrupoService.trasladar_a_grupo(
                persona_x_grupo_id=vinculo.pk,
                nuevo_grupo_id=99999,
                ejecutor=self.ejecutor,
            )

    # ---------- trasladar_a_facultad ----------

    def test_trasladar_a_facultad_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        trasladado = PersonaXGrupoService.trasladar_a_facultad(
            persona_x_grupo_id=vinculo.pk,
            nueva_facultad_id=self.facultad_b.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(trasladado.facultad, self.facultad_b)

    def test_trasladar_a_facultad_vinculacion_de_grupo_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        # Este vínculo tiene grupo != None, así que no es de tipo "facultad" puro.
        # Aun así facultad_id no es None, por lo que la validación de tipo pasa;
        # se prueba entonces el caso realista: vínculo puro de grupo (facultad=None).
        vinculo.facultad = None
        vinculo.save(update_fields=["facultad"])
        with self.assertRaises(ValueError):
            PersonaXGrupoService.trasladar_a_facultad(
                persona_x_grupo_id=vinculo.pk,
                nueva_facultad_id=self.facultad_b.pk,
                ejecutor=self.ejecutor,
            )

    def test_trasladar_a_facultad_inexistente_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValueError):
            PersonaXGrupoService.trasladar_a_facultad(
                persona_x_grupo_id=vinculo.pk,
                nueva_facultad_id=99999,
                ejecutor=self.ejecutor,
            )

    # ---------- cambiar_rol ----------

    def test_cambiar_rol_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        actualizado = PersonaXGrupoService.cambiar_rol(
            persona_x_grupo_id=vinculo.pk,
            nuevo_rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.rol_grupo, self.rol_investigador)

    def test_cambiar_rol_inexistente_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValueError):
            PersonaXGrupoService.cambiar_rol(
                persona_x_grupo_id=vinculo.pk,
                nuevo_rol_grupo_id=99999,
                ejecutor=self.ejecutor,
            )

    # ---------- eliminar / reactivar ----------

    def test_eliminar_desvincula_y_registra_fecha(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        eliminado = PersonaXGrupoService.eliminar(
            vinculo.pk, ejecutor=self.ejecutor, desvinculacion=date(2024, 6, 1)
        )
        self.assertFalse(eliminado.estado)
        self.assertEqual(eliminado.desvinculacion, date(2024, 6, 1))

    def test_eliminar_fecha_anterior_a_vinculacion_falla(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 6, 1),
        )
        with self.assertRaises(ValidationError):
            PersonaXGrupoService.eliminar(
                vinculo.pk, ejecutor=self.ejecutor, desvinculacion=date(2024, 1, 1)
            )

    def test_reactivar_exitoso(self):
        vinculo = PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        PersonaXGrupoService.eliminar(vinculo.pk, ejecutor=self.ejecutor)
        reactivado = PersonaXGrupoService.reactivar(vinculo.pk, ejecutor=self.ejecutor)
        self.assertTrue(reactivado.estado)
        self.assertIsNone(reactivado.desvinculacion)

    # ---------- consultas ----------

    def test_es_administrativo_true_sin_grupo_ni_facultad(self):
        PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            vinculacion=date(2024, 1, 1),
        )
        self.assertTrue(PersonaXGrupoService.es_administrativo(self.persona.pk))

    def test_pertenece_a_grupo_true(self):
        PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        self.assertTrue(PersonaXGrupoService.pertenece_a_grupo(self.persona.pk))

    def test_obtener_facultad_activa(self):
        PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_tutor.pk,
            ejecutor=self.ejecutor,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        facultad = PersonaXGrupoService.obtener_facultad_activa(self.persona.pk)
        self.assertEqual(facultad, self.facultad_a)

    def test_obtener_grupo_activo(self):
        PersonaXGrupoService.crear(
            persona_id=self.persona.pk,
            rol_grupo_id=self.rol_investigador.pk,
            ejecutor=self.ejecutor,
            grupo_id=self.grupo_a.pk,
            facultad_id=self.facultad_a.pk,
            vinculacion=date(2024, 1, 1),
        )
        grupo = PersonaXGrupoService.obtener_grupo_activo(self.persona.pk)
        self.assertEqual(grupo, self.grupo_a)