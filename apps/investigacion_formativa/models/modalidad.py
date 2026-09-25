from django.db import models

class Modalidad(models.Model):
    nombre = models.CharField(max_length=150, unique=True, help_text="Nombre de la modalidad (ej. 'Trabajo de Grado Pregrado', 'Semilleros de Investigación').")
    codigo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)    
    activo = models.BooleanField(default=True)
    requiere_evaluadores = models.BooleanField(default=False)
    requiere_tutor = models.BooleanField(null=True)
    requiere_antiplagio = models.BooleanField(null=True)
    requiere_sustentacion = models.BooleanField(null=True)
    cantidad_maxima_estudiantes = models.FloatField(null=True, blank=True)
    cantidad_minima_evaluadores = models.IntegerField(null=True, blank=True)
    permite_homologacion = models.BooleanField(null=True)
    requiere_producto_final = models.BooleanField(null=True)
    
    class Meta:
        verbose_name = "Modalidad"
        verbose_name_plural = "Modalidades"

    def __str__(self):
        return self.nombre