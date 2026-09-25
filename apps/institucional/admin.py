from django.contrib import admin
from .models import (
    Persona,
    GradoEstudios,
    GrupoInvestigacion,
    FacultadEscuela,
    FacultadXGrupo,
    PersonaXGrupo,
    RolGrupo,
    Gerente,
)

# ======================================================
# PERSONA
# ======================================================

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'grado__sigla_grado', 'nombre',  'apellido', 'documento', 'celular', 'correo')
    search_fields = ('grado__sigla_grado', 'nombre',  'apellido', 'documento', 'celular', 'correo')
    list_filter = ('nombre', 'apellido', 'documento', 'celular', 'correo')
    ordering = ('apellido', 'nombre')


# ======================================================
# GRADO DE ESTUDIOS
# ======================================================

@admin.register(GradoEstudios)
class GradoEstudiosAdmin(admin.ModelAdmin):
    list_display = ('id', 'sigla_grado')
    search_fields = ('sigla_grado',)


# ======================================================
# FACULTAD ESCUELA
# ======================================================

@admin.register(FacultadEscuela)
class FacultadEscuelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_facultad', 'abreviatura')
    search_fields = ('nombre_facultad', 'abreviatura')
    list_filter = ('nombre_facultad', 'abreviatura')


# ======================================================
# GRUPO DE INVESTIGACIÓN
# ======================================================

@admin.register(GrupoInvestigacion)
class GrupoInvestigacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_grupo', 'sigla_grupo')
    search_fields = ('nombre_grupo', 'sigla_grupo')
    list_filter = ('nombre_grupo', 'sigla_grupo')


# ======================================================
# RELACIÓN FACULTAD - GRUPO
# ======================================================

@admin.register(FacultadXGrupo)
class FacultadXGrupoAdmin(admin.ModelAdmin):
    list_display = ('id','grupo__sigla_grupo', 'facultad__abreviatura')
    search_fields = ('facultad__abreviatura', 'grupo__sigla_grupo')
    list_filter = ('facultad__abreviatura', 'grupo__sigla_grupo')


# ======================================================
# ROL EN GRUPO
# ======================================================

@admin.register(RolGrupo)
class RolGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cargo')
    search_fields = ('cargo',)


# ======================================================
# RELACIÓN PERSONA - GRUPO
# ======================================================

@admin.register(PersonaXGrupo)
class PersonaXGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona__documento', 'rol_grupo__cargo', 'grupo__sigla_grupo', 'facultad__abreviatura', 'estado')
    search_fields = ('persona__documento', 'rol_grupo__cargo', 'grupo__sigla_grupo', 'facultad__abreviatura', 'estado')
    list_filter = ('persona__documento', 'rol_grupo__cargo', 'grupo__sigla_grupo', 'facultad__abreviatura', 'estado')


# ======================================================
# GERENTE
# ======================================================

@admin.register(Gerente)
class GerenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona__documento', 'fecha_ingreso', 'fecha_salida', 'estado')
    search_fields = ('persona__documento', 'fecha_ingreso', 'fecha_salida', 'estado')
    list_filter = ('persona__documento', 'fecha_ingreso', 'fecha_salida', 'estado')
