from apps.investigacion_formativa.models import Estudiante


class EstudianteSelector:

    @staticmethod
    def listar():
        return (
            Estudiante.objects
            .select_related('persona', 'modalidad_facultad__facultad', 'modalidad_facultad__modalidad')
            .order_by('persona__apellido', 'persona__nombre')
        )

    @staticmethod
    def obtener(estudiante_id):
        return Estudiante.objects.get(pk=estudiante_id)
    
    @staticmethod
    def existe(estudiante_id):
        return Estudiante.objects.filter(pk=estudiante_id).exists()
    
    @staticmethod
    def existe_persona(persona_id, excluir_id=None):
        """Valida el OneToOneField Estudiante.persona antes de crear/actualizar:
        una Persona no puede tener más de un registro Estudiante, sin importar
        la modalidad."""
        qs = Estudiante.objects.filter(persona_id=persona_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_modalidad_facultad(modalidad_facultad_id, estado=None):
        qs = Estudiante.objects.filter(modalidad_facultad_id=modalidad_facultad_id)
        if estado is not None:
            qs = qs.filter(estado=estado)
        return qs.select_related('persona').order_by('persona__apellido')

    @staticmethod
    def listar_por_facultad(facultad_id, estado=None):
        qs = Estudiante.objects.filter(modalidad_facultad__facultad_id=facultad_id)
        if estado is not None:
            qs = qs.filter(estado=estado)
        return qs.select_related('persona', 'modalidad_facultad__modalidad').order_by('persona__apellido')

    @staticmethod
    def listar_por_modalidad(modalidad_id, estado=None):
        qs = Estudiante.objects.filter(modalidad_facultad__modalidad_id=modalidad_id)
        if estado is not None:
            qs = qs.filter(estado=estado)
        return qs.select_related('persona', 'modalidad_facultad__facultad').order_by('persona__apellido')