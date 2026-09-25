from django.db import models

class GrupoMinciencias(models.Model): 
    nombre_grupo_minciencias = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre_grupo_minciencias