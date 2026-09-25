from django.db import models

class ProcesoFormativo(models.Model):
    idea = models.ForeignKey("investigacion_formativa.BancoIdeas", on_delete=models.SET_NULL, null=True, blank=True)
    flujo_version = models.ForeignKey("investigacion_formativa.FlujoProceso", on_delete=models.PROTECT, null=True, help_text="Versión del flujo de trabajo con que inició el proceso")
    entidad_externa = models.ForeignKey('crm.EntidadExterna', null=True, blank=True, on_delete=models.SET_NULL)
    titulo = models.CharField(max_length=500, null=True)
    nota_final = models.FloatField(null=True, blank=True)
    aprobado = models.BooleanField(null=True)
    estado_general = models.CharField(max_length=255)
    porcentaje_avance = models.FloatField(null=True, blank=True)
    horas_acumuladas = models.FloatField(null=True, blank=True)
    requiere_sustentacion = models.BooleanField(null=True)
    permite_segunda_instancia = models.BooleanField(null=True)
    segunda_instancia_consumida = models.BooleanField(null=True)
    observacion = models.TextField(help_text="El tema o área en la que estará enmarcado el proyecto")
    palabras_clave = models.CharField(max_length=200, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_creacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    @property
    def estado_actual(self):
        etapas = self.instanciaetapa_set.all().order_by('etapa__orden')

        if not etapas.exists():
            return "SIN_INICIAR"

        if any(e.estado == "SEGUNDA_INSTANCIA" for e in etapas):
            return "SEGUNDA_INSTANCIA"

        if all(e.estado == "APROBADO" for e in etapas):
            return "FINALIZADO"

        if any(e.estado == "EN_PROCESO" for e in etapas):
            return "EN_PROCESO"

        if any(e.estado == "RECHAZADO" for e in etapas):
            return "RECHAZADO"

        return "PENDIENTE"
    
    @property
    def modalidad(self):
        return self.flujo_version.modalidad
    
    class Meta:
        verbose_name = "Proceso Formativo"
        verbose_name_plural = "Procesos Formativos"
        ordering = ['-fecha_creacion']        

    def __str__(self):
        return f"{self.titulo}"