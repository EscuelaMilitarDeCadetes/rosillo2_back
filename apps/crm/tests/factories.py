from django.utils import timezone

from apps.usuarios.models import Usuario
from apps.institucional.models import (
    Persona,
    Gerente,
    GradoEstudios,
)
from apps.investigacion_formal.models import Proyecto


class ProyectoFactory:
    """
    Factory propia para los tests del módulo CRM.

    Crea automáticamente:

        GradoEstudios
            ↓
        Persona
            ↓
        Gerente
            ↓
        Usuario
            ↓
        Proyecto

    El objetivo es que los tests únicamente hagan:

        ProyectoFactory.create()

    sin preocuparse por las dependencias.
    """

    _contador = 1

    @classmethod
    def create(cls, titulo="Proyecto prueba"):

        numero = cls._contador
        cls._contador += 1

        grado = cls._crear_grado(numero)
        persona = cls._crear_persona(grado, numero)
        gerente = cls._crear_gerente(persona)
        usuario = cls._crear_usuario(numero)

        return Proyecto.objects.create(
            usuario=usuario,
            gerente=gerente,
            titulo=f"{titulo} {numero}",
            interno=True,
            registro_acta_cierre=False,
            alianza=False,
            estado=True,
            estado_aprobado="APROBADO",
            financiado=False,
            unidad_ejecutora="ESMIC",
            linea_investigacion="IA",
            codigo=f"PR-{numero:04d}",
        )

    @staticmethod
    def _crear_grado(numero):

        return GradoEstudios.objects.create(
            sigla_grado=f"G{numero}",
            descripcion=f"Grado {numero}",
        )

    @staticmethod
    def _crear_persona(grado, numero):

        return Persona.objects.create(
            grado=grado,
            nombre=f"Nombre{numero}",
            apellido=f"Apellido{numero}",
            documento=f"1000000{numero}",
            celular=f"3000000{numero:03d}",
            correo=f"persona{numero}@esmic.edu.co",
        )

    @staticmethod
    def _crear_gerente(persona):

        return Gerente.objects.create(
            persona=persona,
            fecha_ingreso=timezone.now().date(),
            estado=True,
        )

    @staticmethod
    def _crear_usuario(numero):

        return Usuario.objects.create_user(
            username=f"usuario{numero}@esmic.edu.co",
            email=f"usuario{numero}@esmic.edu.co",
            password="admin123",
        )