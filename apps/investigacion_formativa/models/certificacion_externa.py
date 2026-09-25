from django.db import models

class CertificacionExterna(models.Model):
    TIPO_CHOICES = [
        ("MINOR", "Minor"),
        ("DIPLOMADO", "Diplomado de profundización"),
        ("CATEDRA_INTERNACIONAL", "Cátedra internacional"),
        ("OTRO", "Otro"),
    ]

    proceso = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="certificaciones_externas")
    certificado_asistencia = models.ForeignKey("common.DocumentoFirma", null=True, blank=True, on_delete=models.SET_NULL, related_name="certificaciones_asistencia", help_text="Certificado de constancia de asistencia (paso previo)")
    certificado_aprobacion = models.ForeignKey("common.DocumentoFirma", null=True, blank=True, on_delete=models.SET_NULL, related_name="certificaciones_aprobacion", help_text="Certificado de aprobación final cargado por facultades")
    validado_por = models.ForeignKey("usuarios.Usuario", null=True, blank=True, on_delete=models.SET_NULL, related_name="certificaciones_validadas")
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    nombre_programa = models.CharField(max_length=255)
    institucion = models.CharField(max_length=200)
    horas_certificadas = models.FloatField(help_text="Horas certificadas por la institución")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()    
    horas_validadas = models.FloatField(default=0, help_text="Horas formalmente validadas por el rol facultades")
    cumple_horas = models.BooleanField(default=False, help_text="True cuando horas_validadas >= 120")    
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Certificación Externa"
        verbose_name_plural = "Certificaciones Externas"

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nombre_programa}"