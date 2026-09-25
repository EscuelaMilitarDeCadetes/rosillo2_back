# apps/investigacion_formativa/selectors/modalidad_x_facultad_selector.py
from apps.investigacion_formativa.models import ModalidadXFacultad


class ModalidadXFacultadSelector:

    @staticmethod
    def listar():
        return (
            ModalidadXFacultad.objects
            .select_related('facultad', 'modalidad')
            .order_by('facultad', 'modalidad')
        )

    @staticmethod
    def obtener(modalidad_facultad_id):
        return ModalidadXFacultad.objects.get(pk=modalidad_facultad_id)
    
    @staticmethod
    def existe(modalidad_facultad_id):
        return ModalidadXFacultad.objects.filter(pk=modalidad_facultad_id).exists()

    @staticmethod
    def existe_facultad_modalidad(facultad_id, modalidad_id, excluir_id=None):
        """Valida unique_together ('facultad', 'modalidad') antes de crear/actualizar."""
        qs = ModalidadXFacultad.objects.filter(facultad_id=facultad_id, modalidad_id=modalidad_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_facultad(facultad_id, disponible=None):
        qs = ModalidadXFacultad.objects.select_related('modalidad').filter(facultad_id=facultad_id)
        if disponible is not None:
            qs = qs.filter(disponible=disponible)
        return qs.order_by('modalidad__nombre')