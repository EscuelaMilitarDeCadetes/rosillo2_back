
from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.institucional.views import (
    PersonaViewSet,
    GradoEstudiosViewSet,
    GrupoInvestigacionViewSet,
    FacultadEscuelaViewSet,
    FacultadXGrupoViewSet,
    PersonaXGrupoViewSet,
    RolGrupoViewSet,
    GerenteViewSet,
    MiPerfilView,
)

router = DefaultRouter()
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'grados', GradoEstudiosViewSet, basename='grado-estudios')
router.register(r'grupos', GrupoInvestigacionViewSet, basename='grupo-investigacion')
router.register(r'facultades', FacultadEscuelaViewSet, basename='facultad-escuela')
router.register(r'facultad-grupo', FacultadXGrupoViewSet, basename='facultad-x-grupo')
router.register(r'persona-grupo', PersonaXGrupoViewSet, basename='persona-x-grupo')
router.register(r'roles-grupo', RolGrupoViewSet, basename='rol-grupo')
router.register(r'gerentes', GerenteViewSet, basename='gerente')

urlpatterns = router.urls + [
    path("mi-perfil/", MiPerfilView.as_view(), name="mi-perfil"),
]