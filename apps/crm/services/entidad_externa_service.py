from django.db import transaction
from apps.crm.models import EntidadExterna
from apps.crm.selectors.entidad_externa_selector import EntidadExternaSelector
from apps.crm.validators.entidad_externa_validator import EntidadExternaValidator
from apps.common.services.historial_service import HistorialService


class EntidadExternaService:

    @staticmethod
    def listar():
        return EntidadExternaSelector.listar()

    @staticmethod
    def obtener(entidad_id):
        return EntidadExternaSelector.obtener(entidad_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre, sector, pais, tipo_relacion, ejecutor):
        EntidadExternaValidator.validar_creacion(nombre, sector, pais, tipo_relacion)
        entidad = EntidadExterna.objects.create(
            nombre=nombre.strip(),
            sector=sector.strip(),
            pais=pais.strip(),
            tipo_relacion=tipo_relacion,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la entidad externa '{entidad.nombre}' "
            f"(sector={entidad.sector}, país={entidad.pais}, "
            f"tipo={entidad.tipo_relacion}, id={entidad.pk}).",
            objeto=entidad,
        )
        return entidad

    @staticmethod
    @transaction.atomic
    def actualizar(entidad_id, ejecutor, nombre=None, sector=None, pais=None, tipo_relacion=None):
        entidad = EntidadExternaSelector.obtener(entidad_id)

        nuevo_nombre = nombre if nombre is not None else entidad.nombre
        nuevo_sector = sector if sector is not None else entidad.sector
        nuevo_pais = pais if pais is not None else entidad.pais
        nuevo_tipo_relacion = tipo_relacion if tipo_relacion is not None else entidad.tipo_relacion

        EntidadExternaValidator.validar_actualizacion(
            entidad_id, nuevo_nombre, nuevo_sector, nuevo_pais, nuevo_tipo_relacion
        )

        entidad.nombre = nuevo_nombre.strip()
        entidad.sector = nuevo_sector.strip()
        entidad.pais = nuevo_pais.strip()
        entidad.tipo_relacion = nuevo_tipo_relacion
        entidad.save(update_fields=["nombre", "sector", "pais", "tipo_relacion"])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizaron los datos de la entidad externa "
            f"'{entidad.nombre}' (id={entidad.pk}).",
            objeto=entidad,
        )
        return entidad

    @staticmethod
    @transaction.atomic
    def eliminar(entidad_id, ejecutor):
        entidad = EntidadExternaSelector.obtener(entidad_id)
        EntidadExternaValidator.validar_eliminacion(entidad)

        nombre = entidad.nombre
        pk = entidad.pk

        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la entidad externa '{nombre}' (id={pk}).",
        )
        entidad.delete()
        return True

    @staticmethod
    def listar_por_tipo_relacion(tipo_relacion):
        return EntidadExternaSelector.listar_por_tipo_relacion(tipo_relacion)

    @staticmethod
    def listar_por_sector(sector):
        return EntidadExternaSelector.listar_por_sector(sector)

    @staticmethod
    def listar_por_pais(pais):
        return EntidadExternaSelector.listar_por_pais(pais)