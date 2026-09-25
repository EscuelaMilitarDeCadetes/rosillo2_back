from django.contrib import admin
from .models import (
    Proyecto,
    Convocatoria,
    ProyectoXConvocatoria,
    TipoProducto,
    ProductoMinciencias,
    GrupoMinciencias,
    ProductoXGrupo,
    ProductoXProyecto,
    TipoCalificacion,
    Calificacion,
    TipoRubro,
    Monto,
    Ejecucion,
    Objetivos,
    ObjetivoXPunto,
    PuntoControl,
    InvestigadorXProyecto,
    RolInvestigador,
    ControlCambios,
)

# ======================================================
# PROYECTOS Y CONVOCATORIAS
# ======================================================

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    def documento_investigador(self, obj):
        return obj.usuario.persona.documento if obj.usuario and hasattr(obj.usuario, 'persona') else None
    documento_investigador.short_description = 'Documento'

    list_display = ('id', 'documento_investigador', 'titulo', 'interno', 'registro_acta_cierre', 'alianza', 'estado', 'estado_aprobado', 'financiado', 'unidad_ejecutora', 'linea_investigacion', 'fecha_inicio', 'fecha_fin', 'codigo', 'gruplac')
    search_fields = ('usuario__persona__documento', 'titulo', 'interno', 'registro_acta_cierre', 'alianza', 'estado', 'estado_aprobado', 'financiado', 'unidad_ejecutora', 'linea_investigacion', 'fecha_inicio', 'fecha_fin', 'codigo', 'gruplac')
    list_filter = ('usuario', 'titulo', 'interno', 'registro_acta_cierre', 'alianza', 'estado', 'estado_aprobado', 'financiado', 'unidad_ejecutora', 'linea_investigacion', 'fecha_inicio', 'fecha_fin', 'codigo', 'gruplac')
    ordering = ('-fecha_inicio',)


@admin.register(Convocatoria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_convocatoria', 'anio_convocatoria', 'inicio', 'cierre', 'estado', 'interno')
    search_fields = ('nombre_convocatoria', 'anio_convocatoria', 'inicio', 'cierre', 'estado', 'interno')
    list_filter = ('nombre_convocatoria', 'anio_convocatoria', 'inicio', 'cierre', 'estado', 'interno')


@admin.register(ProyectoXConvocatoria)
class ProyectoXConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'convocatoria__nombre_convocatoria', 'proyecto__titulo', 'estado', 'estado_finalizado_calificacion', 'ultimo_filtro_calificacion', 'aprobacion_ultima_calificacion', 'calificacion_ultimo_filtro_calificacion', 'modificacion_documento_proyecto')
    search_fields = ('convocatoria__nombre_convocatoria', 'proyecto__titulo', 'estado', 'estado_finalizado_calificacion', 'ultimo_filtro_calificacion', 'aprobacion_ultima_calificacion', 'calificacion_ultimo_filtro_calificacion', 'modificacion_documento_proyecto')
    list_filter = ('convocatoria__nombre_convocatoria', 'proyecto__titulo', 'estado', 'estado_finalizado_calificacion', 'ultimo_filtro_calificacion', 'aprobacion_ultima_calificacion', 'calificacion_ultimo_filtro_calificacion', 'modificacion_documento_proyecto')


# ======================================================
# PRODUCTOS Y MINCIENCIAS
# ======================================================

@admin.register(TipoProducto)
class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_producto', 'aplica')
    search_fields = ('tipo_producto', 'aplica')
    list_filter = ('tipo_producto', 'aplica')


@admin.register(ProductoMinciencias)
class ProductoMincienciasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_producto', 'nomenclatura', 'peso', 'vigencia')
    search_fields = ('nombre_producto', 'nomenclatura', 'peso', 'vigencia')
    list_filter = ('nombre_producto', 'nomenclatura', 'peso', 'vigencia')


@admin.register(GrupoMinciencias)
class GrupoMincienciasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_grupo_minciencias')
    search_fields = ('nombre_grupo_minciencias',)
    list_filter = ('nombre_grupo_minciencias',)


@admin.register(ProductoXGrupo)
class ProductoXGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_minciencias__nombre_producto', 'grupo_minciencias__nombre_grupo_minciencias', 'tipo_producto__tipo_producto')
    search_fields = ('producto_minciencias__nombre_producto', 'grupo_minciencias__nombre_grupo_minciencias', 'tipo_producto__tipo_producto')
    list_filter = ('producto_minciencias__nombre_producto', 'grupo_minciencias__nombre_grupo_minciencias', 'tipo_producto__tipo_producto')


@admin.register(ProductoXProyecto)
class ProductoXProyectoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_x_grupo__producto_minciencias__nombre_producto', 'producto_x_grupo__grupo_minciencias__nombre_grupo_minciencias', 'proyecto__titulo', 'activo', 'entregado', 'categoria', 'puntaje', 'gruplac')
    search_fields = ('producto_x_grupo__producto_minciencias__nombre_producto', 'producto_x_grupo__grupo_minciencias__nombre_grupo_minciencias', 'proyecto__titulo', 'activo', 'entregado', 'categoria', 'puntaje', 'gruplac')
    list_filter = ('producto_x_grupo__producto_minciencias__nombre_producto', 'producto_x_grupo__grupo_minciencias__nombre_grupo_minciencias', 'proyecto__titulo', 'activo', 'entregado', 'categoria', 'puntaje', 'gruplac')


# ======================================================
# CALIFICACIONES
# ======================================================

@admin.register(TipoCalificacion)
class TipoCalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_calificacion', 'descripcion', 'evaluacion', 'orden_fase')
    search_fields = ('tipo_calificacion', 'evaluacion', 'orden_fase')
    list_filter = ('tipo_calificacion', 'evaluacion', 'orden_fase')



@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'fase__tipo_calificacion', 'aplicar__proyecto__titulo', 'aplicar__convocatoria__nombre_convocatoria', 'aprobado')
    search_fields = ('fase__tipo_calificacion', 'aplicar__proyecto__titulo', 'aplicar__convocatoria__nombre_convocatoria', 'aprobado',)
    list_filter = ('fase__tipo_calificacion', 'aplicar__proyecto__titulo', 'aplicar__convocatoria__nombre_convocatoria', 'aprobado',)


# ======================================================
# PRESUPUESTO Y EJECUCIÓN
# ======================================================

@admin.register(TipoRubro)
class TipoRubroAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_rubro')
    search_fields = ('nombre_rubro',)


@admin.register(Monto)
class MontoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto__titulo', 'solicitado', 'aprobado', 'asignado', 'ejecutado', 'contrapartida', 'total')
    search_fields = ('proyecto__titulo', 'solicitado', 'aprobado', 'asignado', 'ejecutado', 'contrapartida', 'total')
    list_filter = ('proyecto__titulo', 'solicitado', 'aprobado', 'asignado', 'ejecutado', 'contrapartida', 'total')


@admin.register(Ejecucion)
class EjecucionAdmin(admin.ModelAdmin):
    list_display = ('id', 'monto__proyecto__titulo', 'tipo_rubro__nombre_rubro', 'nombre', 'costo', 'descripcion', 'estado')
    search_fields = ('monto__proyecto__titulo', 'tipo_rubro__nombre_rubro', 'nombre', 'costo', 'descripcion', 'estado')
    list_filter = ('monto__proyecto__titulo', 'tipo_rubro__nombre_rubro', 'nombre', 'costo', 'descripcion', 'estado')


# ======================================================
# OBJETIVOS Y CONTROL
# ======================================================

@admin.register(Objetivos)
class ObjetivosAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto__titulo', 'objetivo', 'clase', 'estado')
    search_fields = ('proyecto__titulo', 'objetivo', 'clase', 'estado')
    list_filter = ('proyecto__titulo', 'objetivo', 'clase', 'estado')


@admin.register(PuntoControl)
class PuntoControlAdmin(admin.ModelAdmin):
    list_display = ('id', 'control', 'peso', 'completado', 'estado')
    search_fields = ('control', 'peso', 'completado', 'estado')
    list_filter = ('control', 'peso', 'completado', 'estado')


@admin.register(ObjetivoXPunto)
class ObjetivoXPuntoAdmin(admin.ModelAdmin):
    list_display = ('id', 'objetivo__proyecto__titulo', 'punto_control__control', 'descripcion_avance', 'avance', 'mes_avance', 'anio_avance', 'estado')
    list_filter = ('objetivo__proyecto__titulo', 'punto_control__control', 'descripcion_avance', 'avance', 'mes_avance', 'anio_avance', 'estado')
    search_fields = ('objetivo__proyecto__titulo', 'punto_control__control', 'descripcion_avance', 'avance', 'mes_avance', 'anio_avance', 'estado')


# ======================================================
# INVESTIGADORES
# ======================================================

@admin.register(RolInvestigador)
class RolInvestigadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_rol_investigador', 'descripcion')
    search_fields = ('nombre_rol_investigador', 'descripcion')
    list_filter = ('nombre_rol_investigador', 'descripcion')


@admin.register(InvestigadorXProyecto)
class InvestigadorXProyectoAdmin(admin.ModelAdmin):
    list_display = ('id', 'rol_investigador__nombre_rol_investigador', 'proyecto__titulo', 'persona_x_grupo__persona__documento', 'persona_x_grupo__grupo__sigla_grupo', 'persona_x_grupo__facultad__abreviatura', 'estado')
    search_fields = ('rol_investigador__nombre_rol_investigador', 'proyecto__titulo', 'persona_x_grupo__persona__documento', 'persona_x_grupo__grupo__sigla_grupo', 'persona_x_grupo__facultad__abreviatura', 'estado')
    list_filter = ('rol_investigador__nombre_rol_investigador', 'proyecto__titulo', 'persona_x_grupo__persona__documento', 'persona_x_grupo__grupo__sigla_grupo', 'persona_x_grupo__facultad__abreviatura', 'estado')


# ======================================================
# CONTROL DE CAMBIOS
# ======================================================

@admin.register(ControlCambios)
class ControlCambiosAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto__titulo', 'tipo_cambio', 'fecha_cambio', 'cambio_tiempo', 'cambio_investigador', 'cambio_costo', 'cambio_producto')
    search_fields = ('proyecto__titulo', 'tipo_cambio', 'fecha_cambio', 'cambio_tiempo', 'cambio_investigador', 'cambio_costo', 'cambio_producto')
    list_filter = ('proyecto__titulo', 'tipo_cambio', 'fecha_cambio', 'cambio_tiempo', 'cambio_investigador', 'cambio_costo', 'cambio_producto')
    ordering = ('-fecha_cambio',)
