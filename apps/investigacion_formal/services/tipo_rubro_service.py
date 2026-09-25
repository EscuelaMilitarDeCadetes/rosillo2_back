from django.db import transaction

from apps.investigacion_formal.models import TipoRubro
from apps.investigacion_formal.selectors.tipo_rubro_selector import TipoRubroSelector
from apps.investigacion_formal.validators.tipo_rubro_validator import TipoRubroValidator
from apps.common.services.historial_service import HistorialService


class TipoRubroService:

    @staticmethod
    def listar():
        return TipoRubroSelector.listar()
    
    @staticmethod
    def listar_aplicables():
        return TipoRubroSelector.listar_aplicables()

    @staticmethod
    def obtener(tipo_rubro_id):
        return TipoRubroSelector.obtener(tipo_rubro_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_rubro, aplica, ejecutor):
        TipoRubroValidator.validar_creacion(nombre_rubro)
        rubro = TipoRubro.objects.create(nombre_rubro=nombre_rubro.strip(), aplica=bool(aplica))
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el tipo de rubro '{rubro.nombre_rubro}' "
            f"(id={rubro.pk}, aplica={rubro.aplica}).",
            objeto=rubro,
        )
        return rubro

    @staticmethod
    @transaction.atomic
    def actualizar(tipo_rubro_id, nombre_rubro, aplica, ejecutor):
        rubro = TipoRubroSelector.obtener(tipo_rubro_id)
        TipoRubroValidator.validar_actualizacion(tipo_rubro_id, nombre_rubro)
        rubro.nombre_rubro = nombre_rubro.strip()
        rubro.aplica = bool(aplica)
        rubro.save(update_fields=['nombre_rubro', 'aplica'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el tipo de rubro '{rubro.nombre_rubro}' "
            f"(id={rubro.pk}, aplica={rubro.aplica}).",
            objeto=rubro,
        )
        return rubro