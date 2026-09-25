from django.db import models

class EntidadExterna(models.Model):
    nombre = models.CharField(max_length=255)
    sector = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    tipo_relacion = models.CharField(max_length=50, choices=[('FINANCIADOR', 'Financiador'), ('COOPERANTE', 'Cooperante')])
    
    class Meta:
        verbose_name = "Entidad Externa"
        verbose_name_plural = "Entidades Externas"
    
    def __str__(self):
        return self.nombre