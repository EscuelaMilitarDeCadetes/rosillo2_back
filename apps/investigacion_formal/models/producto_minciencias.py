from django.db import models

class ProductoMinciencias(models.Model):
    nombre_producto = models.CharField(max_length=200, unique=True)
    nomenclatura = models.CharField(max_length=20, unique=True)
    peso = models.IntegerField()
    vigencia = models.IntegerField()

    def __str__(self):
        return self.nombre_producto