from django.db import models

class PlantillaDocumento(models.Model): 
    tipo_documento = models.ForeignKey("common.TipoDocumento", on_delete=models.CASCADE)
    ruta_documento = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tipo_documento',)
    
    def __str__(self):
        return f"{self.tipo_documento.nombre_documento}"