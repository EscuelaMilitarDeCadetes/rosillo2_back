# apps/investigacion_formativa/tests/base.py
import itertools
from datetime import date
from apps.usuarios.models import RolPlataforma, RolXUsuario
from apps.usuarios.models import Usuario
from apps.institucional.models import GradoEstudios, Persona, FacultadEscuela
from apps.common.models import TipoDocumento, DocumentoFirma
from apps.investigacion_formativa.models import (
    Modalidad, FlujoProceso, EtapaFlujo, BancoIdeas, ProcesoFormativo, InstanciaEtapa,
    ModalidadXFacultad, ParticipanteProceso,
)
from apps.investigacion_formativa.services.evaluacion_proceso_service import (
    EvaluacionProcesoService,
)
from django.core.cache import cache

_contador_persona = itertools.count(1)


class InvestigacionFormativaFixturesMixin:

    def setUp(self):
        cache.clear()
        self.ejecutor = Usuario.objects.create_user(
            username='cinterno@esmic.edu.co',
            email='cinterno@esmic.edu.co',
            password='cinterno123',
        )
        rol_soporte, _ = RolPlataforma.objects.get_or_create(
            nombre_rol='SOPORTE', defaults={'descripcion': 'Soporte'},
        )
        RolXUsuario.objects.create(usuario=self.ejecutor, rol=rol_soporte, estado=True)
        self.grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.persona = Persona.objects.create(
            grado=self.grado, nombre='Ana', apellido='Gómez',
            documento='100200300', celular='3009876543', correo='ana@esmic.edu.co',
        )
        self.facultad = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Ingeniería', abreviatura='ING'
        )
        self.modalidad = Modalidad.objects.create(
            nombre='Trabajo de Grado Pregrado',
            codigo='TGP',
            activo=True,
            requiere_evaluadores=True,
            requiere_tutor=True,
            requiere_antiplagio=True,
            requiere_sustentacion=True,
            permite_homologacion=False,
            requiere_producto_final=True,
        )
        self.flujo = FlujoProceso.objects.create(
            modalidad=self.modalidad,
            nombre='Flujo Trabajo de Grado Pregrado v1',
            version=1,
            tipo='FORMATIVA',
            activo=True,
            fecha_vigencia_inicio=date(2024, 1, 1),
        )
        self.idea = BancoIdeas.objects.create(
            facultad=self.facultad,
            idea='Idea semilla de prueba',
            descripcion='Descripción de prueba',
            linea_investigacion='Tecnología',
            palabras_clave='pruebas, django',
            estado='DISPONIBLE',
        )
        self.modalidad_facultad = ModalidadXFacultad.objects.create(
            facultad=self.facultad, modalidad=self.modalidad,
        )
        self.modalidad_x_facultad = self.modalidad_facultad  # alias: algunos tests usan este nombre
        self.proceso = self._crear_proceso_formativo()

        # Flujo APARTE (no self.flujo) para no chocar con tests que crean
        # sus propias etapas con orden=1/2 directamente sobre self.flujo
        # (unique_together en EtapaFlujo es (flujo, orden)).
        self.flujo_transiciones = FlujoProceso.objects.create(
            modalidad=self.modalidad,
            nombre='Flujo Transiciones v1',
            version=2,
            tipo='FORMATIVA',
            activo=True,
            fecha_vigencia_inicio=date(2024, 1, 1),
        )
        # Dos etapas del mismo flujo, usadas como origen/destino por los
        # tests de ReglaFlujo, TransicionFlujo, InstanciaEtapa y SegundaInstancia.
        self.etapa_origen = self._crear_etapa_flujo(
            flujo=self.flujo_transiciones, orden=1, nombre='Etapa Origen', rol_responsable='ESTUDIANTE'
        )
        self.etapa_destino = self._crear_etapa_flujo(
            flujo=self.flujo_transiciones, orden=2, nombre='Etapa Destino', rol_responsable='TUTOR'
        )
        # Instancia "base" del proceso en la etapa de origen. Los tests que
        # necesitan crear una segunda instancia (InstanciaEtapa tiene
        # unique_together en proceso+etapa) usan self.etapa_destino para no chocar
        self.instancia_etapa = self._crear_instancia_etapa(self.proceso, self.etapa_origen)
        # Participante "base" del proceso (rol ESTUDIANTE, la propia self.persona)
        self.participante = InvestigacionFormativaFixturesMixin._crear_participante(
            self, self.proceso, rol_en_modalidad='ESTUDIANTE', persona=self.persona
        )
        # Evaluación "base" sobre self.instancia_etapa, usada por SegundaInstancia
        # y por cualquier test que necesite una evaluación ya existente.
        self.tutor_evaluador = InvestigacionFormativaFixturesMixin._crear_participante(
            self, self.proceso, rol_en_modalidad='TUTOR'
        )
        self.evaluacion = EvaluacionProcesoService.crear(
            evaluador_id=self.tutor_evaluador.pk,
            instancia_etapa_id=self.instancia_etapa.pk,
            concepto='Evaluación base de la fixture',
            aprobado=True,
            nota=4.0,
            tipo_evaluador='TUTOR',
            tipo_evaluacion='SEGUIMIENTO',
            peso=1.0,
            resultado='APROBADO',
            ejecutor=self.ejecutor,
        )
        super().setUp()

    def _crear_proceso_formativo(self, titulo='Proceso de prueba', flujo_version=None, idea=None,
                                  fecha_inicio=None, fecha_fin=None, activo=True):
        return ProcesoFormativo.objects.create(
            idea=idea if idea is not None else self.idea,
            flujo_version=flujo_version or self.flujo,
            titulo=titulo,
            estado_general='EN_PROCESO',
            observacion='Observación de prueba',
            fecha_inicio=fecha_inicio or date(2024, 1, 1),
            fecha_fin=fecha_fin or date(2024, 12, 31),
            activo=activo,
        )

    def _crear_etapa_flujo(self, flujo=None, orden=1, nombre='Etapa 1',
                            rol_responsable='ESTUDIANTE', es_final=False, codigo=None):
        return EtapaFlujo.objects.create(
            flujo=flujo or self.flujo,
            nombre=nombre,
            orden=orden,
            codigo=f'ETP-{orden}',
            rol_responsable=rol_responsable,
            es_final=es_final,
        )

    def _crear_persona(self, nombre='Persona', apellido='Prueba', documento=None,
                        celular=None, correo=None, grado=None):
        n = next(_contador_persona)
        return Persona.objects.create(
            grado=grado or self.grado,
            nombre=nombre,
            apellido=apellido,
            documento=documento or f'DOCTEST{n:06d}',
            celular=celular or f'3000000{n:04d}',
            correo=correo or f'persona{n}@esmic.edu.co',
        )

    def _crear_facultad(self, nombre='Facultad de Prueba', abreviatura='FDP'):
        return FacultadEscuela.objects.create(
            nombre_facultad=nombre, abreviatura=abreviatura,
        )

    def _crear_participante(self, proceso, rol_en_modalidad='ESTUDIANTE', persona=None):
        persona = persona or self._crear_persona()
        return ParticipanteProceso.objects.create(
            proceso_formativo=proceso,
            persona=persona,
            rol_en_modalidad=rol_en_modalidad,
        )

    def _crear_instancia_etapa(self, proceso, etapa, estado='PENDIENTE'):
        return InstanciaEtapa.objects.create(proceso=proceso, etapa=etapa, estado=estado)

    def _crear_banco_idea(self, facultad=None, idea='Otra idea', estado='DISPONIBLE'):
        return BancoIdeas.objects.create(
            facultad=facultad or self.facultad,
            idea=idea,
            descripcion='Descripción',
            linea_investigacion='Línea',
            palabras_clave='clave',
            estado=estado,
        )

    def _crear_documento_firma(self, nombre_documento='Documento de prueba'):
        tipo_documento = TipoDocumento.objects.create(
            nombre_documento=nombre_documento, grupo='INVESTIGACION_FORMATIVA'
        )
        return DocumentoFirma.objects.create(
            tipo_documento=tipo_documento,
            version=1,
            ruta_documento='/documentos/prueba.pdf',
            hash_documento='0' * 64,
            ip_creacion='127.0.0.1',
        )