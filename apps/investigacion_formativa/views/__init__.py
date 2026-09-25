from .actividad_formativa_viewset import ActividadFormativaViewSet
from .banco_ideas_viewset import BancoIdeasViewSet
from .certificacion_externa_viewset import CertificacionExternaViewSet
from .estadisticas_viewset import EstadisticasViewSet
from .estudiante_viewset import EstudianteViewSet
from .etapa_flujo_viewset import EtapaFlujoViewSet
from .evaluacion_proceso_viewset import EvaluacionProcesoViewSet
from .evento_evaluativo_viewset import EventoEvaluativoViewSet
from .flujo_proceso_viewset import FlujoProcesoViewSet
from .homologacion_viewset import HomologacionViewSet
from .instancia_etapa_viewset import InstanciaEtapaViewSet
from .modalidad_viewset import ModalidadViewSet
from .modalidad_x_facultad_viewset import ModalidadXFacultadViewSet
from .participante_proceso_viewset import ParticipanteProcesoViewSet
from .plan_trabajo_viewset import PlanTrabajoViewSet
from .postulacion_proceso_viewset import PostulacionProcesoViewSet
from .proceso_formativo_viewset import ProcesoFormativoViewSet
from .proceso_formativo_x_proyecto_viewset import ProcesoFormativoXProyectoViewSet
from .registro_actividades_viewset import RegistroActividadesViewSet
from .registro_horas_viewset import RegistroHorasViewSet
from .regla_flujo_viewset import ReglaFlujoViewSet
from .requisito_modalidad_viewset import RequisitoModalidadViewSet
from .revision_viewset import RevisionViewSet
from .segunda_instancia_viewset import SegundaInstanciaViewSet
from .transicion_flujo_viewset import TransicionFlujoViewSet
from .tutor_viewset import TutorViewSet
from .validacion_antiplagio_viewset import ValidacionAntiplagioViewSet


__all__ = [
    "ActividadFormativaViewSet",
    "BancoIdeasViewSet",
    "CertificacionExternaViewSet",
    "EstadisticasViewSet",
    "EstudianteViewSet",
    "EtapaFlujoViewSet",
    "EvaluacionProcesoViewSet",
    "EventoEvaluativoViewSet",
    "FlujoProcesoViewSet",
    "HomologacionViewSet",
    "InstanciaEtapaViewSet",
    "ModalidadViewSet",
    "ModalidadXFacultadViewSet",
    "ParticipanteProcesoViewSet",
    "PlanTrabajoViewSet",
    "PostulacionProcesoViewSet",
    "ProcesoFormativoViewSet",
    "ProcesoFormativoXProyectoViewSet",
    "RegistroActividadesViewSet",
    "RegistroHorasViewSet",
    "ReglaFlujoViewSet",
    "RequisitoModalidadViewSet",
    "RevisionViewSet",
    "SegundaInstanciaViewSet",
    "TransicionFlujoViewSet",
    "TutorViewSet",
    "ValidacionAntiplagioViewSet",
]