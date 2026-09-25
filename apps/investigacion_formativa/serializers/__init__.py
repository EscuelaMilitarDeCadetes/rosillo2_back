from .actividad_formativa_serializer import ActividadFormativaSerializer
from .avance_serializer import AvanceProcesoFormativoSerializer, EtapaActualSerializer, UltimoRegistroAvanceSerializer
from .banco_ideas_serializer import BancoIdeasSerializer
from .certificacion_externa_serializer import CertificacionExternaSerializer
from .estudiante_serializer import EstudianteSerializer
from .etapa_flujo_serializer import EtapaFlujoSerializer
from .evaluacion_proceso_serializer import EvaluacionProcesoSerializer
from .evento_evaluativo_serializer import EventoEvaluativoSerializer
from .flujo_proceso_serializer import FlujoProcesoSerializer
from .homologacion_serializer import HomologacionSerializer
from .instancia_etapa_serializer import InstanciaEtapaSerializer
from .modalidad_serializer import ModalidadSerializer
from .modalidad_x_facultad_serializer import ModalidadXFacultadSerializer
from .plan_trabajo_serializer import PlanTrabajoSerializer
from .postulacion_proceso_serializer import PostulacionProcesoSerializer
from .proceso_formativo_serializer import ProcesoFormativoSerializer
from .proceso_formativo_x_proyecto_serializer import ProcesoFormativoXProyectoSerializer
from .registro_actividades_serializer import RegistroActividadesSerializer
from .registro_horas_serializer import RegistroHorasSerializer
from .regla_flujo_serializer import ReglaFlujoSerializer
from .requisito_modalidad_serializer import RequisitoModalidadSerializer
from .revision_serializer import RevisionSerializer
from .segunda_instancia_serializer import SegundaInstanciaSerializer
from .transicion_flujo_serializer import TransicionFlujoSerializer
from .tutor_serializer import TutorSerializer
from .validacion_antiplagio_serializer import ValidacionAntiplagioSerializer

__all__ = [
    "ActividadFormativaSerializer",
    "AvanceProcesoFormativoSerializer",
    "BancoIdeasSerializer",
    "CertificacionExternaSerializer",
    "EstudianteSerializer",
    "EtapaActualSerializer",
    "EtapaFlujoSerializer",
    "EvaluacionProcesoSerializer",
    "EventoEvaluativoSerializer",
    "FlujoProcesoSerializer",
    "HomologacionSerializer",
    "InstanciaEtapaSerializer",
    "ModalidadSerializer",
    "ModalidadXFacultadSerializer",
    "PlanTrabajoSerializer",
    "PostulacionProcesoSerializer",
    "ProcesoFormativoSerializer",
    "ProcesoFormativoXProyectoSerializer",
    "RegistroActividadesSerializer",
    "RegistroHorasSerializer",
    "ReglaFlujoSerializer",
    "RequisitoModalidadSerializer",
    "RevisionSerializer",
    "SegundaInstanciaSerializer",
    "TransicionFlujoSerializer",
    "TutorSerializer",
    "UltimoRegistroAvanceSerializer",
    "ValidacionAntiplagioSerializer",
]