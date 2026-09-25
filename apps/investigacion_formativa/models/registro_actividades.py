# apps/investigacion_formativa/models/registro_actividades.py

from django.db import models
from django.db.models import Q


class RegistroActividades(models.Model):

    TIPO_PERIODO = [
        ("MENSUAL", "Mensual"),
        ("SEMESTRAL", "Semestral"),
        ("PUNTUAL", "Registro puntual"),
    ]

    proceso = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="registros_actividades")
    registrado_por = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True)
    documento = models.ForeignKey("common.DocumentoFirma", null=True, blank=True, on_delete=models.SET_NULL, help_text="Documento firmado asociado al registro")
    tipo_periodo = models.CharField(max_length=15, choices=TIPO_PERIODO)
    fecha_periodo = models.DateField(null=True, blank=True, help_text="Mes o semestre al que corresponde el registro")
    actividades = models.TextField(help_text="Descripción de las actividades realizadas en el período")
    horas_reportadas = models.FloatField(default=0, help_text="Horas trabajadas en este período (para modalidades con requisito de horas)")
    nota = models.FloatField(null=True, blank=True, help_text="Nota del período si aplica (Modalidad 1: nota del tutor)")
    aprobado = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proceso', 'registrado_por', 'fecha_periodo'],
                condition=Q(activo=True),
                name='registro_actividades_unico_periodo_activo',
            )
        ]
        verbose_name = "Registro de Actividades"
        verbose_name_plural = "Registros de Actividades"

    def __str__(self):
        return f"Registro {self.get_tipo_periodo_display()} — {self.proceso.titulo}"