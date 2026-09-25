from django.db import models

class ReglaFlujo(models.Model):
    TIPOS_REGLA = [
        ('NOTA_MINIMA', 'Nota Mínima de Aprobación'),
        ('PORCENTAJE_ANTIPLAGIO_MAX', 'Porcentaje Máximo de Antiplagio'),
        ('HORAS_MINIMAS', 'Horas Mínimas Cumplidas'),
        ('PROMEDIO_MINIMO', 'Promedio Académico Mínimo'),
        ('PRODUCTO_CTEI_REQUERIDO', 'Producto CTeI Requerido'),
        ('EVENTO_CIENTIFICO_REQUERIDO', 'Participación en Evento Científico'),
        ('TIEMPO_MAXIMO_ETAPA', 'Tiempo Máximo para Etapa'),
        ('OTRO', 'Otro'),
    ]
    OPERADORES = [
        ('GT', '>'), ('LT', '<'), ('EQ', '='), ('GTE', '>='), ('LTE', '<='), ('NE', '!='),
    ]

    etapa_origen = models.ForeignKey("investigacion_formativa.EtapaFlujo", related_name='salidas', on_delete=models.CASCADE)
    etapa_destino = models.ForeignKey("investigacion_formativa.EtapaFlujo", related_name='entradas', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    operador = models.CharField(max_length=5, choices=OPERADORES)
    tipo_regla = models.CharField(max_length=50, choices=TIPOS_REGLA)
    valor_minimo = models.FloatField()
    valor_maximo = models.FloatField()
    mensaje_error = models.CharField(max_length=200)
    accion_resultado = models.CharField(max_length=50)
    bloqueante = models.BooleanField(default=False)
    prioridad = models.IntegerField(default=1)
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField()
    
    class Meta:
        unique_together = ('etapa_origen', 'etapa_destino', 'nombre')
        verbose_name = "Regla de Proceso de Grado"
        verbose_name_plural = "Reglas de Proceso de Grado"
    
    def __str__(self):
        return f"{self.etapa_origen} -> {self.etapa_destino}"