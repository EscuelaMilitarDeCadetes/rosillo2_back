from django.db import models


class EjecucionTareaProgramada(models.Model):
    """
    Registro de la última corrida de cada tarea diaria que ejecuta el
    programador interno (apps/common/programador.py). Sirve para que:
      - una tarea no se ejecute dos veces el mismo día (aunque el servidor
        se reinicie o haya más de un proceso), y
      - si el servidor estaba apagado a la hora programada, la tarea se
        ejecute apenas vuelva a arrancar ese mismo día.
    """
    nombre = models.CharField(max_length=100, unique=True)
    ultima_fecha = models.DateField(null=True, blank=True)
    ultima_ejecucion = models.DateTimeField(null=True, blank=True)
    ultimo_resultado = models.TextField(blank=True, default='')
    ultimo_error = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ejecución de tarea programada'
        verbose_name_plural = 'Ejecuciones de tareas programadas'

    def __str__(self):
        return f"{self.nombre} (última: {self.ultima_fecha})"
