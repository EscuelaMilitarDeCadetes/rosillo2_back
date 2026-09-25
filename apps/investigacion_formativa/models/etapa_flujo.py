from django.db import models

class EtapaFlujo(models.Model):
    TIPOS_ETAPA = [
        ('INICIO', 'Inicio de Proceso'),
        ('CARGA_DOC', 'Carga de Documento'),
        ('APROBACION', 'Aprobación'),
        ('EVALUACION', 'Evaluación'),
        ('REVISION', 'Revisión/Corrección'),
        ('SEGUIMIENTO', 'Seguimiento'),
        ('SUSTENTACION', 'Sustentación'),
        ('CIERRE', 'Cierre de Proceso'),
        ('OTRO', 'Otro'),
    ]

    flujo = models.ForeignKey("investigacion_formativa.FlujoProceso", on_delete=models.CASCADE, related_name="etapas")
    documento_requerido = models.ForeignKey("common.TipoDocumento", on_delete=models.SET_NULL, null=True, blank=True, help_text="Formato que se debe cargar en esta etapa")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(help_text="Orden secuencial de la etapa dentro del flujo.")
    codigo = models.CharField(max_length=100)
    tipo_etapa = models.CharField(max_length=20, choices=TIPOS_ETAPA, default='OTRO')
    es_obligatoria = models.BooleanField(default=True)
    permite_paralelismo = models.BooleanField(default=True)
    permite_reversion = models.BooleanField(default=True)
    permite_salto = models.BooleanField(default=True)
    requiere_aprobacion = models.BooleanField(default=True)
    requiere_documento = models.BooleanField(default=True)
    requiere_firma = models.BooleanField(default=True)
    requiere_evaluacion = models.BooleanField(default=True)    
    es_final = models.BooleanField(default=False, help_text="Indica si esta etapa es una etapa final del flujo.")
    rol_responsable = models.CharField(
        max_length=20,
        choices=[
            ("ESTUDIANTE", "Estudiante"),
            ("TUTOR", "Tutor"),
            ("JURADO", "Jurado"),
            ("FACULTAD", "Facultad"),
        ]
    )
    permite_reintentos = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Etapa de Flujo"
        verbose_name_plural = "Etapas de Flujo"
        unique_together = ('flujo', 'orden')
        ordering = ['flujo', 'orden']

    def __str__(self):
        return f"{self.flujo.nombre} — {self.orden}. {self.nombre}"