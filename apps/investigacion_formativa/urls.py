from rest_framework.routers import DefaultRouter


from apps.investigacion_formativa.views import *


router = DefaultRouter()


router.register(r'actividad-formativa', ActividadFormativaViewSet, basename='actividad-formativa')
router.register(r'banco-ideas', BancoIdeasViewSet, basename='banco-ideas')
router.register(r'certificacion-externa', CertificacionExternaViewSet, basename='certificacion-externa')
router.register(r'estadisticas', EstadisticasViewSet, basename='estadisticas-formativa')
router.register(r'estudiante', EstudianteViewSet, basename='estudiante')
router.register(r'etapa-flujo', EtapaFlujoViewSet, basename='etapa-flujo')
router.register(r'evaluacion-proceso', EvaluacionProcesoViewSet, basename='evaluacion-proceso')
router.register(r'evento-evaluativo', EventoEvaluativoViewSet, basename='evento-evaluativo')
router.register(r'flujo-proceso', FlujoProcesoViewSet, basename='flujo-proceso')
router.register(r'homologacion', HomologacionViewSet, basename='homologacion')
router.register(r'instancia-etapa', InstanciaEtapaViewSet, basename='instancia-etapa')
router.register(r'modalidad-facultad', ModalidadXFacultadViewSet, basename='modalidad-facultad')
router.register(r'modalidad', ModalidadViewSet, basename='modalidad')
router.register(r'participante-proceso', ParticipanteProcesoViewSet, basename='participante-proceso')
router.register(r'plan-trabajo', PlanTrabajoViewSet, basename='plan-trabajo')
router.register(r'postulacion-proceso', PostulacionProcesoViewSet, basename='postulacion-proceso')
router.register(r'proceso-formativo-proyecto', ProcesoFormativoXProyectoViewSet, basename='proceso-formativo-proyecto')
router.register(r'proceso-formativo', ProcesoFormativoViewSet, basename='proceso-formativo')
router.register(r'registro-actividades', RegistroActividadesViewSet, basename='registro-actividades')
router.register(r'registro-horas', RegistroHorasViewSet, basename='registro-horas')
router.register(r'regla-flujo', ReglaFlujoViewSet, basename='regla-flujo')
router.register(r'requisito-modalidad', RequisitoModalidadViewSet, basename='requisito-modalidad')
router.register(r'revision', RevisionViewSet, basename='revision')
router.register(r'segunda-instancia', SegundaInstanciaViewSet, basename='segunda-instancia')
router.register(r'transicion-flujo', TransicionFlujoViewSet, basename='transicion-flujo')
router.register(r'tutor', TutorViewSet, basename='tutor')
router.register(r'validacion-antiplagio', ValidacionAntiplagioViewSet, basename='validacion-antiplagio')


urlpatterns = router.urls