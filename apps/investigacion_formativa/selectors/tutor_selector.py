from apps.investigacion_formativa.models import Tutor


class TutorSelector:

    @staticmethod
    def listar():
        return Tutor.objects.select_related('persona', 'facultad').all()

    @staticmethod
    def obtener(tutor_id):
        return Tutor.objects.select_related('persona', 'facultad').get(pk=tutor_id)

    @staticmethod
    def existe_para_persona(persona_id):
        return Tutor.objects.filter(persona_id=persona_id).exists()

    @staticmethod
    def existe_para_persona_y_facultad(persona_id, facultad_id, excluir_id=None):
        qs = Tutor.objects.filter(persona_id=persona_id, facultad_id=facultad_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_activos_por_facultad(facultad_id):
        return (
            Tutor.objects
            .select_related('persona')
            .filter(facultad_id=facultad_id, estado=True)
        )