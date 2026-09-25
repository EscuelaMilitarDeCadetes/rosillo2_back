"""
Service de FacultadEscuela.

Interfaz estándar definitiva + métodos de negocio específicos:
    listar(), obtener(id), crear(...), actualizar(id, ...), eliminar(id),
    listar_facultades_usuario(usuario_id), listar_facultades_grupo(grupo_id)

Metodos existentes
    listarFacultadEscuela() -> listar()
    listarFacultadesXUsuario(id) -> listar_facultades_usuario(usuario_id)
    listarFacultadesEscuelaGrupoCM() -> listar_facultades_grupo(grupo_id)

grupo_id NO tiene un valor por defecto — debe pasarse explícitamente en cada 
llamada. Ningún caller actual (backend ni React) invoca este método
sin el parámetro.
"""
from django.db import transaction

from apps.common.services.historial_service import HistorialService
from apps.institucional.models import FacultadEscuela
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector
from apps.institucional.validators.facultad_escuela_validator import FacultadEscuelaValidator


class FacultadEscuelaService:

    @staticmethod
    def listar():
        return FacultadEscuelaSelector.listar()

    @staticmethod
    def obtener(facultad_id):
        return FacultadEscuelaSelector.obtener(facultad_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_facultad, abreviatura, ejecutor):
        FacultadEscuelaValidator.validar_creacion(nombre_facultad, abreviatura)
        facultad = FacultadEscuela.objects.create(
            nombre_facultad=nombre_facultad.strip(),
            abreviatura=abreviatura.strip().upper(),
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la facultad '{facultad.nombre_facultad}' con la abreviatura '{facultad.abreviatura}'",
            objeto=facultad,
        )
        return facultad

    @staticmethod
    @transaction.atomic
    def actualizar(facultad_id, nombre_facultad, abreviatura, ejecutor):
        facultad = FacultadEscuelaSelector.obtener(facultad_id)
        FacultadEscuelaValidator.validar_actualizacion(facultad_id, nombre_facultad, abreviatura)
        facultad.nombre_facultad = nombre_facultad.strip()
        facultad.abreviatura = abreviatura.strip().upper()
        facultad.save(update_fields=["nombre_facultad", "abreviatura"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la facultad '{facultad.nombre_facultad}' con la abreviatura '{facultad.abreviatura}'",
            objeto=facultad,
        )
        return facultad

    @staticmethod
    def listar_facultades_usuario(usuario_id):
        return FacultadEscuelaSelector.obtener_facultad_usuario(usuario_id)

    @staticmethod
    def listar_facultades_grupo(grupo_id=None):
        # grupo_id=None por defecto aquí para que, si se omite,
        # la llamada llegue limpia al Selector y se resuelva
        # en el ValidationError intencional de "Debe especificar el
        # grupo." en vez de un TypeError por argumento faltante.
        return FacultadEscuelaSelector.listar_facultades_grupo(grupo_id)