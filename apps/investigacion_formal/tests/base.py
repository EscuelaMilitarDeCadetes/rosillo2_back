import itertools

from apps.usuarios.models import Usuario
from apps.institucional.models import (
    GradoEstudios, Persona, PersonaXGrupo, RolGrupo,
    GrupoInvestigacion, FacultadEscuela, FacultadXGrupo, Gerente,
)
from apps.investigacion_formal.models import (
    Proyecto, Convocatoria, TipoCalificacion, TipoRubro,
    RolInvestigador, Monto, ProyectoXConvocatoria,
)
from django.core.cache import cache


class InvestigacionFormalFixturesMixin:
    
    def setUp(self):
        cache.clear()
        self._contador_proyecto = itertools.count(1)
        self._contador_convocatoria = itertools.count(1)

        self.ejecutor = Usuario.objects.create_user(
            username='cinterno@esmic.edu.co',
            email='cinterno@esmic.edu.co',
            password='cinterno123',
        )
        self.usuario_proyecto = Usuario.objects.create_user(
            username='investigador@esmic.edu.co',
            email='investigador@esmic.edu.co',
            password='investigador123',
        )
        self.grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.persona = Persona.objects.create(
            grado=self.grado, nombre='Juan', apellido='Pérez',
            documento='123456789', celular='3001234567', correo='juan@esmic.edu.co',
        )
        self.facultad = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Ingeniería', abreviatura='ING'
        )
        self.grupo = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo de Pruebas', sigla_grupo='GP'
        )
        FacultadXGrupo.objects.create(grupo=self.grupo, facultad=self.facultad)
        self.rol_grupo = RolGrupo.objects.create(cargo='Investigador')
        self.persona_x_grupo = PersonaXGrupo.objects.create(
            persona=self.persona, rol_grupo=self.rol_grupo, grupo=self.grupo,
            vinculacion='2024-01-01', estado=True,
        )
        self.gerente = Gerente.objects.create(persona=self.persona, estado=True)

        # Proyecto "canónico" del test, atado a self.usuario_proyecto/self.gerente.
        # _crear_monto() y helpers similares lo usan por defecto para que
        # varias llamadas dentro del MISMO test caigan en el mismo proyecto
        # (p.ej. mover una ejecución de un monto a otro dentro del mismo proyecto).
        self.proyecto = self._crear_proyecto(usuario=self.usuario_proyecto, gerente=self.gerente)

        super().setUp()

    def _crear_proyecto(self, titulo=None, interno=True, usuario=None, gerente=None):
        """
        Proyecto tiene unique_together=('usuario', 'gerente') y titulo único.
        Si se pasa usuario/gerente explícito, se usa tal cual (o el default
        self.usuario_proyecto/self.gerente si falta alguno).
        Si NO se pasa ninguno, se entiende que el llamador quiere un proyecto
        genuinamente distinto ("otro proyecto") y se genera una pareja
        investigador/gerente nueva, más un título único si tampoco se dio.
        """
        if usuario is None and gerente is None:
            n = next(self._contador_proyecto)
            usuario = Usuario.objects.create_user(
                username=f'investigador{n}@esmic.edu.co',
                email=f'investigador{n}@esmic.edu.co',
                password='investigador123',
            )
            persona = Persona.objects.create(
                grado=self.grado, nombre=f'Investigador{n}', apellido='Prueba',
                documento=f'9999900{n:03d}', celular=f'30000000{n}',
                correo=f'investigador{n}@esmic.edu.co',
            )
            gerente = Gerente.objects.create(persona=persona, estado=True)
            if titulo is None:
                titulo = f'Proyecto de prueba {n}'
        else:
            usuario = usuario or self.usuario_proyecto
            gerente = gerente or self.gerente
            if titulo is None:
                titulo = 'Proyecto de prueba'

        return Proyecto.objects.create(
            usuario=usuario,
            gerente=gerente,
            titulo=titulo,
            interno=interno,
            registro_acta_cierre=False,
            alianza=False,
            estado=True,
            estado_aprobado='SIN_CALIFICAR',
            financiado=False,
            unidad_ejecutora='ING',
            linea_investigacion='Tecnología',
            codigo='',
            gruplac=False,
        )

    def _crear_convocatoria(self, nombre=None, interno=True,
                             inicio='2024-01-01', cierre='2024-12-31'):
        if nombre is None:
            n = next(self._contador_convocatoria)
            nombre = 'Convocatoria 2024' if n == 1 else f'Convocatoria 2024 ({n})'
        return Convocatoria.objects.create(
            nombre_convocatoria=nombre,
            anio_convocatoria=2024,
            inicio=inicio,
            cierre=cierre,
            estado=True,
            interno=interno,
        )

    def _crear_tipo_calificacion(self, nombre='Fase 1', orden=1, evaluacion=False):
        return TipoCalificacion.objects.create(
            tipo_calificacion=nombre,
            descripcion=f'Descripción {nombre}',
            evaluacion=evaluacion,
            orden_fase=orden,
        )

    def _crear_proyecto_x_convocatoria(self, proyecto=None, convocatoria=None):
        proyecto = proyecto or self.proyecto
        convocatoria = convocatoria or self._crear_convocatoria()
        return ProyectoXConvocatoria.objects.create(
            proyecto=proyecto,
            convocatoria=convocatoria,
            estado=True,
        )

    def _crear_tipo_rubro(self, nombre='Personal'):
        return TipoRubro.objects.create(nombre_rubro=nombre)

    def _crear_monto(self, proyecto=None, solicitado=1000000):
        proyecto = proyecto or self.proyecto
        return Monto.objects.create(
            proyecto=proyecto, solicitado=solicitado, aprobado=0,
            ejecutado=0, contrapartida=0, total=0,
        )

    def _crear_rol_investigador(self, nombre='Investigador Principal'):
        return RolInvestigador.objects.create(
            nombre_rol_investigador=nombre, descripcion='Rol de prueba'
        )