from django.db import models
from apps.usuarios.ambitos import AMBITO_FORMAL, AMBITO_FORMATIVA

class TipoDocumento(models.Model):
    INVESTIGACION_CHOICES = [
        (AMBITO_FORMAL, "Formal"),
        (AMBITO_FORMATIVA, "Formativa"),
    ]
    nombre_documento = models.CharField(max_length=40, unique=True)
    grupo = models.CharField(max_length=30)
    investigacion = models.CharField(max_length=10, choices=INVESTIGACION_CHOICES, null=True, blank=True)
    es_obligatorio = models.BooleanField(default=False)
    
    es_acta_inicio = models.BooleanField(default=False)
    es_informe_seguimiento = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre_documento