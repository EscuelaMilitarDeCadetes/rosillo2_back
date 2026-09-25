from django.db import models

class TipoProducto(models.Model):
    tipo_producto = models.CharField(max_length=200, unique=True)
    aplica = models.BooleanField(default=False)

    def __str__(self):
        return self.tipo_producto