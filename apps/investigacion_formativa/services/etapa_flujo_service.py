# apps/investigacion_formativa/services/etapa_flujo_service.py
from django.db import transaction

from apps.investigacion_formativa.models import EtapaFlujo
from apps.investigacion_formativa.selectors.etapa_flujo_selector import EtapaFlujoSelector
from apps.investigacion_formativa.validators.etapa_flujo_validator import EtapaFlujoValidator
from apps.common.services.historial_service import HistorialService


class EtapaFlujoService:
    """Los métodos activar()/desactivar() controlan el campo `activo` de la
    etapa, sin afectar su vínculo con FlujoProceso."""

    @staticmethod
    def listar():
        return EtapaFlujoSelector.listar()

    @staticmethod
    def obtener(etapa_id):
        return EtapaFlujoSelector.obtener(etapa_id)

    @staticmethod
    def listar_por_flujo(flujo_id):
        return EtapaFlujoSelector.listar_por_flujo(flujo_id)

    @staticmethod
    @transaction.atomic
    def crear(flujo_id, nombre, orden, codigo, rol_responsable, ejecutor,
              documento_requerido_id=None, descripcion=None, tipo_etapa='OTRO',
              es_obligatoria=True, permite_paralelismo=True, permite_reversion=True,
              permite_salto=True, requiere_aprobacion=True, requiere_documento=False,
              requiere_firma=True, requiere_evaluacion=True, es_final=False,
              permite_reintentos=True):
        EtapaFlujoValidator.validar_creacion(
            flujo_id, nombre, orden, codigo, tipo_etapa, rol_responsable,
            documento_requerido_id=documento_requerido_id,
            requiere_documento=requiere_documento,
            es_final=es_final,
            permite_salto=permite_salto,
        )
        etapa = EtapaFlujo.objects.create(
            flujo_id=flujo_id,
            documento_requerido_id=documento_requerido_id,
            nombre=nombre,
            descripcion=descripcion,
            orden=orden,
            codigo=codigo,
            tipo_etapa=tipo_etapa,
            es_obligatoria=es_obligatoria,
            permite_paralelismo=permite_paralelismo,
            permite_reversion=permite_reversion,
            permite_salto=permite_salto,
            requiere_aprobacion=requiere_aprobacion,
            requiere_documento=requiere_documento,
            requiere_firma=requiere_firma,
            requiere_evaluacion=requiere_evaluacion,
            es_final=es_final,
            rol_responsable=rol_responsable,
            permite_reintentos=permite_reintentos,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la etapa '{etapa.nombre}' (orden {etapa.orden}) del flujo "
            f"'{etapa.flujo.nombre}' (id={etapa.id}).",
            objeto=etapa,
        )
        return etapa

    @staticmethod
    @transaction.atomic
    def actualizar(etapa_id, nombre, orden, codigo, rol_responsable, ejecutor,
                    documento_requerido_id=None, descripcion=None, tipo_etapa='OTRO',
                    es_obligatoria=True, permite_paralelismo=True, permite_reversion=True,
                    permite_salto=True, requiere_aprobacion=True, requiere_documento=False,
                    requiere_firma=True, requiere_evaluacion=True, es_final=False,
                    permite_reintentos=True):
        etapa = EtapaFlujoSelector.obtener(etapa_id)
        EtapaFlujoValidator.validar_actualizacion(
            etapa_id, etapa.flujo_id, nombre, orden, codigo, tipo_etapa, rol_responsable,
            documento_requerido_id=documento_requerido_id,
            requiere_documento=requiere_documento,
            es_final=es_final,
            permite_salto=permite_salto,
        )
        etapa.nombre = nombre
        etapa.orden = orden
        etapa.codigo = codigo
        etapa.rol_responsable = rol_responsable
        etapa.documento_requerido_id = documento_requerido_id
        etapa.descripcion = descripcion
        etapa.tipo_etapa = tipo_etapa
        etapa.es_obligatoria = es_obligatoria
        etapa.permite_paralelismo = permite_paralelismo
        etapa.permite_reversion = permite_reversion
        etapa.permite_salto = permite_salto
        etapa.requiere_aprobacion = requiere_aprobacion
        etapa.requiere_documento = requiere_documento
        etapa.requiere_firma = requiere_firma
        etapa.requiere_evaluacion = requiere_evaluacion
        etapa.es_final = es_final
        etapa.permite_reintentos = permite_reintentos
        etapa.save(update_fields=[
            'nombre', 'orden', 'codigo', 'rol_responsable', 'documento_requerido',
            'descripcion', 'tipo_etapa', 'es_obligatoria', 'permite_paralelismo',
            'permite_reversion', 'permite_salto', 'requiere_aprobacion', 'requiere_documento',
            'requiere_firma', 'requiere_evaluacion', 'es_final', 'permite_reintentos',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la etapa '{etapa.nombre}' del flujo '{etapa.flujo.nombre}' (id={etapa_id}).",
            objeto=etapa,
        )
        return etapa

    @staticmethod
    @transaction.atomic
    def activar(etapa_id, ejecutor):
        etapa = EtapaFlujoSelector.obtener(etapa_id)
        etapa.activo = True
        etapa.save(update_fields=['activo'])
        HistorialService.registrar(ejecutor, f"Se activó la etapa '{etapa.nombre}' (id={etapa_id}).", objeto=etapa)
        return etapa

    @staticmethod
    @transaction.atomic
    def desactivar(etapa_id, ejecutor):
        etapa = EtapaFlujoSelector.obtener(etapa_id)
        etapa.activo = False
        etapa.save(update_fields=['activo'])
        HistorialService.registrar(ejecutor, f"Se desactivó la etapa '{etapa.nombre}' (id={etapa_id}).", objeto=etapa)
        return etapa