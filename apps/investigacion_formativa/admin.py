from django.contrib import admin
from .models import (
    ActividadFormativa,
    BancoIdeas,
    CertificacionExterna,
    Estudiante,
    EtapaFlujo,
    EvaluacionProceso,
    EventoEvaluativo,
    FlujoProceso,
    Homologacion,
    InstanciaEtapa,
    ModalidadXFacultad,
    Modalidad,
    ParticipanteProceso,
    PlanTrabajo,
    PostulacionProceso,
    ProcesoFormativoXProyecto,
    ProcesoFormativo,
    RegistroActividades,
    RegistroHoras,
    ReglaFlujo,
    RequisitoModalidad,
    Revision,
    SegundaInstancia,
    TransicionFlujo,
    Tutor,
    ValidacionAntiplagio,
)

# ==============================
# ACTIVIDAD FORMATIVA
# ==============================
@admin.register(ActividadFormativa)
class ActividadFormativaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

# ==============================
# BANCO IDEAS
# ==============================
@admin.register(BancoIdeas)
class BancoIdeasAdmin(admin.ModelAdmin):
    list_display = ('id', 'idea', 'descripcion')
    search_fields = ('idea', 'descripcion')
    ordering = ('idea',)

# ==============================
# CERTIFICACION EXTERNA
# ==============================
@admin.register(CertificacionExterna)
class CertificacionExternaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_programa', 'institucion')
    search_fields = ('nombre_programa', 'institucion')
    ordering = ('nombre_programa',)

# ==============================
# ESTUDIANTE
# ==============================
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'correo_personal', 'nivel')
    search_fields = ('correo_personal', 'nivel')
    ordering = ('correo_personal', 'nivel')

# ==============================
# ETAPA FLUJO
# ==============================
@admin.register(EtapaFlujo)
class EtapaFlujoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'orden', 'codigo')
    search_fields = ('nombre', 'descripcion', 'orden', 'codigo')
    ordering = ('nombre', 'orden', 'codigo')   
    
# ==============================
# EVALUACION PROCESO
# ==============================
@admin.register(EvaluacionProceso)
class EvaluacionProcesoAdmin(admin.ModelAdmin):
    list_display = ('id', 'concepto', 'aprobado', 'peso', 'resultado')
    search_fields = ('concepto', 'aprobado', 'peso', 'resultado')
    ordering = ('concepto', 'peso', 'resultado')

# ==============================
# EVENTO EVALUATIVO
# ==============================
@admin.register(EventoEvaluativo)
class EventoEvaluativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'resultado')
    search_fields = ('numero', 'resultado')
    ordering = ('numero', 'resultado')

# ==============================
# FLUJO PROCESO
# ==============================
@admin.register(FlujoProceso)
class FlujoProcesoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'version', 'tipo')
    search_fields = ('nombre', 'version', 'tipo')
    ordering = ('nombre', 'version', 'tipo')

# ==============================
# HOMOLOGACION
# ==============================
@admin.register(Homologacion)
class HomologacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'observaciones', 'fecha_homologacion')
    search_fields = ('estado', 'observaciones', 'fecha_homologacion')
    ordering = ('estado', 'fecha_homologacion')

# ==============================
# INSTANCIA ETAPA
# ==============================
@admin.register(InstanciaEtapa)
class InstanciaEtapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('estado', 'fecha_inicio', 'fecha_fin')
    ordering = ('estado', 'fecha_inicio', 'fecha_fin')

# ==============================
# MODALIDAD X FACULTAD
# ==============================
@admin.register(ModalidadXFacultad)
class ModalidadXFacultadAdmin(admin.ModelAdmin):
    list_display = ('id', 'modalidad', 'facultad')
    search_fields = ('modalidad__nombre', 'facultad__nombre_facultad')
    ordering = ('modalidad__nombre', 'facultad__nombre_facultad')

# ==============================
# MODALIDAD
# ==============================
@admin.register(Modalidad)
class ModalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'codigo')
    search_fields = ('nombre', 'descripcion', 'codigo')
    ordering = ('nombre', 'codigo')

# ==============================
# PARTICIPANTE PROCESO
# ==============================
@admin.register(ParticipanteProceso)
class ParticipanteProcesoAdmin(admin.ModelAdmin):
    list_display = ('id', 'rol_en_modalidad', 'fecha_asignacion', 'fecha_finalizacion', 'activo')
    search_fields = ('rol_en_modalidad', 'fecha_asignacion', 'fecha_finalizacion', 'activo')
    ordering = ('rol_en_modalidad', 'fecha_asignacion', 'fecha_finalizacion', 'activo')

# ==============================
# PLAN TRABAJO
# ==============================
@admin.register(PlanTrabajo)
class PlanTrabajoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion_general', 'fecha_inicio_planeada', 'fecha_fin_planeada', 'estado', 'observaciones')
    search_fields = ('descripcion_general', 'fecha_inicio_planeada', 'fecha_fin_planeada', 'estado', 'observaciones')
    ordering = ('descripcion_general',)

# ==============================
# POSTULACION PROCESO
# ==============================
@admin.register(PostulacionProceso)
class PostulacionProcesoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'promedio_actual', 'fecha_postulacion', 'fecha_decision')
    search_fields = ('estado', 'promedio_actual', 'fecha_postulacion', 'fecha_decision')
    ordering = ('estado',)

# ==============================
# PROCESO FORMATIVO X PROYECTO
# ==============================
@admin.register(ProcesoFormativoXProyecto)
class ProcesoFormativoXProyectoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proceso_formativo__titulo', 'proyecto_formal__titulo')
    search_fields = ('proceso_formativo__titulo', 'proyecto_formal__titulo')
    ordering = ('proceso_formativo__titulo',)

# ==============================
# PROCESO FORMATIVO
# ==============================
@admin.register(ProcesoFormativo)
class ProcesoFormativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'nota_final', 'aprobado')
    search_fields = ('titulo', 'nota_final', 'aprobado')
    ordering = ('titulo',)

# ==============================
# REGISTRO ACTIVIDADES
# ==============================
@admin.register(RegistroActividades)
class RegistroActividadesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_periodo', 'fecha_periodo', 'horas_reportadas')
    search_fields = ('tipo_periodo', 'fecha_periodo', 'horas_reportadas')
    ordering = ('tipo_periodo',)
    
# ==============================
# REGISTRO HORAS
# ==============================
@admin.register(RegistroHoras)
class RegistroHorasAdmin(admin.ModelAdmin):
    list_display = ('id', 'horas_requeridas', 'horas_acumuladas', 'cumple_requisito')
    search_fields = ('horas_requeridas', 'horas_acumuladas', 'cumple_requisito')
    ordering = ('horas_requeridas',)

# ==============================
# REGLA FLUJO
# ==============================
@admin.register(ReglaFlujo)
class ReglaFlujoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'operador', 'tipo_regla')
    search_fields = ('nombre', 'operador', 'tipo_regla')
    ordering = ('nombre',)

# ==============================
# REQUISITO MODALIDAD
# ==============================
@admin.register(RequisitoModalidad)
class RequisitoModalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'valor_numerico', 'descripcion',)
    search_fields = ('tipo', 'valor_numerico', 'descripcion')
    ordering = ('tipo',)

# ==============================
# REVISION
# ==============================
@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'observaciones', 'aprobado', 'fecha')
    search_fields = ('version', 'observaciones', 'aprobado', 'fecha')
    ordering = ('version',)

# ==============================
# SEGUNDA INSTANCIA
# ==============================
@admin.register(SegundaInstancia)
class SegundaInstanciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'activada', 'consumida', 'tipo', 'motivo', 'nota_maxima', 'fecha_activacion', 'activa')
    search_fields = ('activada', 'consumida', 'tipo', 'motivo', 'nota_maxima', 'fecha_activacion', 'activa')
    ordering = ('activada',)
    
# ==============================
# TRANSICION FLUJO
# ==============================
@admin.register(TransicionFlujo)
class TransicionFlujoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'condicion', 'accion_automatica', 'orden')
    search_fields = ('nombre', 'condicion', 'accion_automatica', 'orden')
    ordering = ('nombre',)

# ==============================
# TUTOR
# ==============================
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'persona__documento', 'estado')
    search_fields = ('persona__documento', 'estado')
    ordering = ('persona__documento',)

# ==============================
# VALIDACION ANTIPLAGIO
# ==============================
@admin.register(ValidacionAntiplagio)
class ValidacionAntiplagioAdmin(admin.ModelAdmin):
    list_display = ('id', 'porcentaje', 'aprobado')
    search_fields = ('porcentaje', 'aprobado')
    ordering = ('porcentaje',)