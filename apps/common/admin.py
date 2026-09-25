from django.contrib import admin
from .models import (
    Aprobacion,
    DocumentoFirma,
    DocumentoFirmante,
    Historial,
    Notificacion,
    PlantillaDocumento,
    Tarea,
    TipoDocumento,
)

# ======================================================
# APROBACION
# ======================================================
@admin.register(Aprobacion)
class AprobacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario_revisor',
        'tipo_documento',
        'id_documento',
        'estado',
        'observacion',
        'fecha_revision',
    )
    search_fields = (
        'usuario_revisor__username',
        'tipo_documento__nombre_documento',
        'id_documento',
        'estado',
        'observacion',
    )
    list_filter = (
        'usuario_revisor__username',
        'tipo_documento__nombre_documento',
        'estado',
    )
    ordering = ('-fecha_revision',)


# ======================================================
# DOCUMENTO FIRMA
# ======================================================
@admin.register(DocumentoFirma)
class DocumentoFirmaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tipo_documento',
        'version',
        'estado',
        'hash_documento',
        'ip_creacion',
        'habilitado_firma',
    )
    search_fields = (
        'tipo_documento__nombre_documento',
        'version',
        'estado',
        'hash_documento',
        'ip_creacion',
    )
    list_filter = (
        'tipo_documento__nombre_documento',
        'estado',
        'habilitado_firma',
    )
    ordering = ('-version',)
    

# ======================================================
# DOCUMENTO FIRMANTE
# ======================================================
@admin.register(DocumentoFirmante)
class DocumentoFirmanteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'documento_firma',
        'usuario',
        'orden',
        'estado',
        'motivo_rechazo',
        'ip_firma',
        'ruta_firma',
        'codigo_verificacion',
        'fecha_firma',
        'fecha_creacion',
    )
    search_fields = (
        'documento_firma__tipo_documento__nombre_documento',
        'usuario__username',
        'orden',
        'estado',
        'motivo_rechazo',
        'ip_firma',
        'ruta_firma',
        'codigo_verificacion',
    )
    list_filter = (
        'documento_firma__tipo_documento__nombre_documento',
        'usuario__username',
        'orden',
        'estado',
    )
    ordering = ('-fecha_creacion',)


# ======================================================
# HISTORIAL
# ======================================================

@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'accion', 'fecha_creacion', 'objeto_relacionado')
    search_fields = ('usuario__username', 'accion')
    list_filter = ('usuario__username', 'accion')
    ordering = ('-fecha_creacion',)




# ======================================================
# NOTIFICACION
# ======================================================

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_destino', 'mensaje', 'tipo', 'leido', 'fecha_creacion', 'url_relacionada')
    search_fields = ('usuario_destino__username', 'mensaje', 'tipo')
    list_filter = ('usuario_destino__username', 'tipo', 'leido')
    ordering = ('-fecha_creacion',)


# ======================================================
# PLANTILLA DOCUMENTO
# ======================================================

@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_documento', 'ruta_documento', 'estado')
    search_fields = ('tipo_documento', 'estado')
    list_filter = ('tipo_documento', 'estado')
    ordering = ('tipo_documento', 'estado')


# ======================================================
# TAREA
# ======================================================

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('id', 'asignado_a', 'descripcion', 'completada', 'fecha_creacion', 'fecha_limite', 'objeto_relacionado')
    search_fields = ('asignado_a__username', 'descripcion', 'completada')
    list_filter = ('asignado_a__username', 'completada')
    ordering = ('-fecha_creacion',)
    

# ======================================================
# TIPO DOCUMENTO
# ======================================================

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_documento', 'grupo', 'investigacion', 'es_obligatorio')
    search_fields = ('nombre_documento',)
    list_filter = ('grupo',)
    ordering = ('nombre_documento',)