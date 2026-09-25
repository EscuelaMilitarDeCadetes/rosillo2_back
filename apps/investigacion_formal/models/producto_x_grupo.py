from django.db import models

class ProductoXGrupo(models.Model):
    producto_minciencias = models.ForeignKey("investigacion_formal.ProductoMinciencias", on_delete=models.CASCADE)
    grupo_minciencias = models.ForeignKey("investigacion_formal.GrupoMinciencias", on_delete=models.CASCADE)
    tipo_producto = models.ForeignKey("investigacion_formal.TipoProducto", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto_minciencias', 'grupo_minciencias', 'tipo_producto')
    
    def __str__(self):
        return f"{self.producto_minciencias} - {self.grupo_minciencias} - {self.tipo_producto}"