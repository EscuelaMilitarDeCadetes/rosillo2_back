from django.contrib import admin
from .models import (Usuario, RolPlataforma, RolXUsuario, UsuarioXPersona)


# ==============================
# USUARIO
# ==============================

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


# ==============================
# ROL PLATAFORMA
# ==============================

@admin.register(RolPlataforma)
class RolPlataformaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_rol', 'descripcion')
    search_fields = ('nombre_rol', 'descripcion')
    ordering = ('nombre_rol',)


# ==============================
# ROL - USUARIO
# ==============================

@admin.register(RolXUsuario)
class RolXUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario__username', 'rol__nombre_rol', 'estado')
    list_filter = ('usuario__username', 'rol__nombre_rol', 'estado')
    search_fields = ('usuario__username', 'rol__nombre_rol', 'estado')


# ==============================
# USUARIO - PERSONA
# ==============================

@admin.register(UsuarioXPersona)
class UsuarioXPersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario__username', 'persona__documento')
    list_filter = ('usuario__username', 'persona__documento')
    search_fields = ('usuario__username', 'persona__documento')
    ordering = ('-fecha_inicio',)