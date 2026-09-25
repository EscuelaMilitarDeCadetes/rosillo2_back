from rest_framework.routers import DefaultRouter
from apps.crm.views import (
    EntidadExternaViewSet,
    IndicadorImpactoViewSet,
    InteraccionViewSet,
)

router = DefaultRouter()
router.register(r'entidad-externa', EntidadExternaViewSet, basename='entidad-externa')
router.register(r'indicador-impacto', IndicadorImpactoViewSet, basename='indicador-impacto')
router.register(r'interaccion', InteraccionViewSet, basename='interaccion')

urlpatterns = router.urls