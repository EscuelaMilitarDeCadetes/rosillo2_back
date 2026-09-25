# apps/investigacion_formativa/models/banco_ideas.py

from django.db import models
from django.db.models import Q


class BancoIdeas(models.Model):

    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('SEPARADA', 'Separada'),
        ('TOMADA', 'Tomada'),
        ('ELIMINADA', 'Eliminada'),
    ]

    facultad = models.ForeignKey('institucional.FacultadEscuela', on_delete=models.CASCADE)
    separada_por = models.ForeignKey(
        'institucional.Persona', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ideas_separadas',
        help_text="Persona que actualmente tiene esta idea separada/tomada.",
    )
    idea = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    linea_investigacion = models.CharField(max_length=255)
    palabras_clave = models.CharField(max_length=255)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='DISPONIBLE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['facultad', 'idea'],
                condition=~Q(estado='ELIMINADA'),
                name='banco_ideas_unica_facultad_idea_activa',
            )
        ]
        verbose_name = "Banco de Ideas"
        verbose_name_plural = "Banco de Ideas"

    def __str__(self):
        return self.idea