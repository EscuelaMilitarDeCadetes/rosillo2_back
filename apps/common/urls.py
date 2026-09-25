from rest_framework.routers import DefaultRouter
from apps.common.views import (
    AprobacionViewSet,
    DocumentoFirmaViewSet,
    DocumentoFirmanteViewSet,
    HistorialViewSet,
    NotificacionViewSet,
    PlantillaDocumentoViewSet,
    SoporteViewSet,
    TareaViewSet,
    TipoDocumentoViewSet,
)

router = DefaultRouter()
router.register(r'aprobacion', AprobacionViewSet, basename='aprobacion')
router.register(r'documento-firma', DocumentoFirmaViewSet, basename='documento-firma')
router.register(r'documento-firmante', DocumentoFirmanteViewSet, basename='documento-firmante')
router.register(r'historial', HistorialViewSet, basename='historial')
router.register(r'notificacion', NotificacionViewSet, basename='notificacion')
router.register(r'plantilla-documento', PlantillaDocumentoViewSet, basename='plantilla-documento')
router.register(r'soporte', SoporteViewSet, basename='soporte')
router.register(r'tarea', TareaViewSet, basename='tarea')
router.register(r'tipos-documento', TipoDocumentoViewSet, basename='tipos-documento')

urlpatterns = router.urls