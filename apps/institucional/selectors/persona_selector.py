"""
Selector de Persona.

mostrarDatosPersona(correo). UsuarioXPersona. obtener_por_correo()
se migra de forma literal contra Persona.correo (que es un campo
propio y real de Persona, independiente de cómo se resuelva el Usuario
asociado).

mostrarTodasPersonas() eso filtraba implícitamente a "personas que 
tienen al menos un PersonaXGrupo". listar() devuelve TODAS las
Personas, sin condición sobre PersonaXGrupo.

filtrar(texto): agregado para soportar búsqueda server-side desde el
frontend (selector paginado de Persona. No reemplaza a listar()
listar() sigue siendo "todas las personas".
"""
from django.db.models import Q
from apps.institucional.models import Persona


class PersonaSelector:

    @staticmethod
    def listar():
        return Persona.objects.select_related('grado').all().order_by('apellido', 'nombre')
    
    @staticmethod
    def filtrar(texto=None):
        """
        Igual que listar(), pero opcionalmente acotado por texto libre
        contra nombre, apellido, documento y correo (icontains, OR).
        texto=None o cadena vacía se comporta igual que listar().
        """
        qs = Persona.objects.select_related('grado').all().order_by('apellido', 'nombre')
        if texto:
            qs = qs.filter(
                Q(nombre__icontains=texto)
                | Q(apellido__icontains=texto)
                | Q(documento__icontains=texto)
                | Q(correo__icontains=texto)
            )
        return qs

    @staticmethod
    def obtener(persona_id):
        return Persona.objects.select_related('grado').get(pk=persona_id)

    @staticmethod
    def existe(persona_id):
        return Persona.objects.filter(pk=persona_id).exists()

    @staticmethod
    def existe_documento(documento, excluir_id=None):
        qs = Persona.objects.filter(documento=documento)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_celular(celular, excluir_id=None):
        qs = Persona.objects.filter(celular=celular)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_correo(correo, excluir_id=None):
        qs = Persona.objects.filter(correo__iexact=correo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()