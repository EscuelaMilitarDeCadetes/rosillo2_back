from django.db import models

class Proyecto(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    gerente = models.ForeignKey('institucional.Gerente', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=2000, unique=True)
    interno = models.BooleanField()
    registro_acta_cierre = models.BooleanField()
    alianza = models.BooleanField()
    estado = models.BooleanField()
    estado_aprobado = models.CharField(max_length=255)
    financiado = models.BooleanField()
    unidad_ejecutora = models.CharField(max_length=10, unique=False)
    linea_investigacion = models.CharField(max_length=100, unique=False)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    codigo = models.CharField(max_length=50)
    gruplac = models.BooleanField(default=False)
    
    grupo_investigacion = models.ForeignKey('institucional.GrupoInvestigacion', on_delete=models.PROTECT, null=True, blank=True, related_name='proyectos_externos')
    facultad = models.ForeignKey('institucional.FacultadEscuela', on_delete=models.PROTECT, null=True, blank=True, related_name='proyectos_externos', help_text="Solo aplica si 'grupo_investigacion' es transversal a varias facultades (ver FacultadXGrupo), p.ej. Ciencias Militares.")

    def __str__(self):
        return f'{self.codigo} {self.titulo}'