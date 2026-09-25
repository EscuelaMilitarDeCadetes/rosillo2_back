from apps.investigacion_formativa.models import RequisitoModalidad


class RequisitoModalidadSelector:

    @staticmethod
    def listar():
        return RequisitoModalidad.objects.select_related('modalidad').all()

    @staticmethod
    def obtener(requisito_id):
        return RequisitoModalidad.objects.select_related('modalidad').get(pk=requisito_id)

    @staticmethod
    def existe_requisito(modalidad_id, tipo, excluir_id=None):
        qs = RequisitoModalidad.objects.filter(modalidad_id=modalidad_id, tipo=tipo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_activos_por_modalidad(modalidad_id):
        return RequisitoModalidad.objects.filter(modalidad_id=modalidad_id, activo=True)