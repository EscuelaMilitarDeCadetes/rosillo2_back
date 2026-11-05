from apps.common.models import PlantillaDocumento


class PlantillaDocumentoSelector:
    @staticmethod
    def listar(investigacion=None):
        qs = PlantillaDocumento.objects.select_related('tipo_documento').filter(estado=True)
        if investigacion is not None:
            qs = qs.filter(tipo_documento__investigacion=investigacion)
        return qs

    @staticmethod
    def obtener(plantilla_id):
        return PlantillaDocumento.objects.select_related('tipo_documento').get(pk=plantilla_id)

    @staticmethod
    def obtener_por_tipo_documento(tipo_documento_id):
        return (
            PlantillaDocumento.objects
            .filter(tipo_documento_id=tipo_documento_id, estado=True)
            .first()
        )

    @staticmethod
    def existe_para_tipo_documento(tipo_documento_id, excluir_id=None):
        qs = PlantillaDocumento.objects.filter(tipo_documento_id=tipo_documento_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()