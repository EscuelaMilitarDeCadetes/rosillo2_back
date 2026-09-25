# apps/investigacion_formativa/models/postulacion_proceso.py

from django.db import models
from django.db.models import Q


class PostulacionProceso(models.Model):

    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("ENVIADA", "Enviada"),
        ("EN_VALIDACION", "En validación de requisitos"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
        ("ELIMINADA", "Eliminada"),
    ]

    estudiante = models.ForeignKey("investigacion_formativa.Estudiante", on_delete=models.CASCADE, related_name="postulaciones")
    modalidad = models.ForeignKey("investigacion_formativa.ModalidadXFacultad", on_delete=models.CASCADE)
    proceso_creado = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.SET_NULL, null=True, blank=True, related_name="postulacion_origen", help_text="Proceso de grado generado al aprobar esta postulación")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="BORRADOR")
    promedio_actual = models.FloatField(help_text="Promedio académico acumulado al momento de la postulación")
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(null=True, blank=True)
    observacion_coordinacion = models.TextField(null=True, blank=True, help_text="Motivo de rechazo o comentarios del coordinador")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'modalidad'],
                condition=~Q(estado='ELIMINADA'),
                name='postulacion_unica_estudiante_modalidad_activa',
            )
        ]
        verbose_name = "Postulación a Proceso de Grado"
        verbose_name_plural = "Postulaciones a Proceso de Grado"

    def __str__(self):
        return f"{self.estudiante} → {self.modalidad.modalidad.nombre} [{self.get_estado_display()}]"