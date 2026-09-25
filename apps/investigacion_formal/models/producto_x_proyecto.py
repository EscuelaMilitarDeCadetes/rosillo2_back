from django.db import models

class ProductoXProyecto(models.Model):
    producto_x_grupo = models.ForeignKey("investigacion_formal.ProductoXGrupo", on_delete=models.CASCADE)
    proyecto = models.ForeignKey("investigacion_formal.Proyecto", on_delete=models.CASCADE)
    activo = models.BooleanField()
    entregado = models.BooleanField()
    categoria = models.CharField(max_length=30)
    puntaje = models.IntegerField()
    gruplac = models.BooleanField(default=False)

    class Meta:
        unique_together = ('producto_x_grupo', 'proyecto')

    def __str__(self):
        return f"{self.producto_x_grupo} - {self.proyecto}"