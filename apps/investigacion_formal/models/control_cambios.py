from django.db import models

class ControlCambios(models.Model):
    proyecto = models.ForeignKey('investigacion_formal.Proyecto', on_delete=models.CASCADE)
    tipo_cambio = models.CharField(max_length=255, unique=False)
    fecha_cambio = models.DateField(null=True, blank=True)
    cambio_tiempo = models.BooleanField(default=False, verbose_name="Tiempo")
    cambio_investigador = models.BooleanField(default=False, verbose_name="Investigador")
    cambio_costo = models.BooleanField(default=False, verbose_name="Costo")
    cambio_producto = models.BooleanField(default=False, verbose_name="Producto")    

    def __str__(self):
        return self.tipo_cambio