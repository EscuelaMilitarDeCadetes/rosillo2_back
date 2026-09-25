from django.db import models

class GrupoInvestigacion(models.Model): 
    nombre_grupo = models.CharField(max_length=50, unique=True)
    sigla_grupo = models.CharField(max_length=8, unique=True)
    clasificacion_grupo = models.CharField(max_length=3, default='')

    def __str__(self):
        return self.nombre_grupo