from rest_framework.routers import DefaultRouter
 
from apps.usuarios.views import (
    UsuarioViewSet,
    RolPlataformaViewSet,
    RolXUsuarioViewSet,
    UsuarioXPersonaViewSet,
    PasswordViewSet,
    LoginFormalView,
    LoginFormativaView,
    LogoutView,
    MeView,
)
 
from rest_framework_simplejwt.views import TokenRefreshView
 
from django.urls import path
 
router = DefaultRouter()
 
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'roles', RolPlataformaViewSet, basename='roles')
router.register(r'roles-usuario', RolXUsuarioViewSet, basename='roles-usuario')
router.register(r'usuario-persona', UsuarioXPersonaViewSet, basename='usuario-persona')
router.register(r'password', PasswordViewSet, basename='password')

urlpatterns = router.urls + [
    path("login/formal/", LoginFormalView.as_view(), name="login-formal"),
    path("login/formativa/", LoginFormativaView.as_view(), name="login-formativa"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),    
    path("me/", MeView.as_view(), name="me"),
]