from django.db import models
from django.db.models import Q


class PersonaXGrupo(models.Model):
    persona = models.ForeignKey("institucional.Persona", on_delete=models.CASCADE)
    rol_grupo = models.ForeignKey("institucional.RolGrupo", on_delete=models.CASCADE)
    grupo = models.ForeignKey("institucional.GrupoInvestigacion", on_delete=models.CASCADE, null=True, blank=True)
    facultad = models.ForeignKey("institucional.FacultadEscuela", on_delete=models.CASCADE, null=True, blank=True)
    vinculacion = models.DateField()
    estado = models.BooleanField(default=True)
    desvinculacion = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            # Investigadores
            models.UniqueConstraint(
                fields=[
                    "persona",
                    "rol_grupo",
                    "grupo",
                ],
                condition=Q(grupo__isnull=False),
                name="uq_persona_rol_grupo",
            ),
            # Facultad
            models.UniqueConstraint(
                fields=[
                    "persona",
                    "rol_grupo",
                    "facultad",
                ],
                condition=Q(
                    grupo__isnull=True,
                    facultad__isnull=False,
                ),
                name="uq_persona_rol_facultad",
            ),
            # Administrativo
            models.UniqueConstraint(
                fields=[
                    "persona",
                    "rol_grupo",
                ],
                condition=Q(
                    grupo__isnull=True,
                    facultad__isnull=True,
                ),
                name="uq_persona_rol_administrativo",
            ),
        ]

    def __str__(self):
        return (
            f"{self.persona} - "
            f"{self.rol_grupo} - "
            f"{self.grupo} - "
            f"{self.facultad}"
        )