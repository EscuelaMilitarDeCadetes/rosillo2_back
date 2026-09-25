"""
URLs del módulo integracion.

Registrar en el urls.py principal de rosillo así:

    path('api/integracion/', include('apps.integracion.urls')),

Endpoints disponibles (todos POST, todos requieren JWT + rol apropiado):

    POST /api/integracion/crear-soporte/            -> VinculacionService.crear_usuario_soporte()
    POST /api/integracion/crear-supervisor/         -> VinculacionService.crear_usuario_supervisor()
    POST /api/integracion/crear-gerente/            -> VinculacionService.crear_usuario_gerente()
    POST /api/integracion/crear-decano/             -> VinculacionService.crear_usuario_decano()
    POST /api/integracion/crear-facultad/           -> VinculacionService.crear_usuario_facultad()
    POST /api/integracion/crear-grupo/              -> VinculacionService.crear_usuario_grupo()
    POST /api/integracion/crear-cinterno/           -> VinculacionService.crear_usuario_cinterno()
    POST /api/integracion/crear-cexterno/           -> VinculacionService.crear_usuario_cexterno()
    POST /api/integracion/crear-asesor/             -> VinculacionService.crear_usuario_asesor()
    POST /api/integracion/crear-estudiante/         -> VinculacionService.crear_usuario_estudiante()
    POST /api/integracion/crear-jurado/             -> VinculacionService.crear_usuario_jurado()
    POST /api/integracion/crear-tutor/              -> VinculacionService.crear_usuario_tutor()
    POST /api/integracion/reemplazar/               -> VinculacionService.reemplazar_usuario()
    POST /api/integracion/retirar/                  -> VinculacionService.retirar_usuario()
    POST /api/integracion/asignar-rol-existente/    -> VinculacionService.asignar_rol_existente()
"""
from rest_framework.routers import DefaultRouter
from apps.integracion.views.vinculacion_viewset import VinculacionViewSet

router = DefaultRouter()
router.register(r'', VinculacionViewSet, basename='vinculacion')

urlpatterns = router.urls