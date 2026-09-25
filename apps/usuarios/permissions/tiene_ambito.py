# E:\PROYECTO_ROSILLO\django_react\django\rosillo\apps\usuarios\permissions\tiene_ambito.py
"""
Valida el claim 'ambito' embebido en el access token (ver auth_views.py y
ambitos.py). Se usa en get_permissions() de CADA ViewSet de
investigacion_formal / investigacion_formativa, sumado (AND, no OR) a la
clase de rol que ya existía — DRF exige que TODOS los permission_classes
devueltos en la lista se cumplan, así que basta con agregar la instancia
correspondiente a la lista sin tocar 'combinar()'.

Ejemplo dentro de un ViewSet de investigacion_formal:
    return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

request.auth es la instancia de AccessToken ya validada por
JWTAuthentication (soporta acceso tipo dict vía .get()), así que no hace
falta volver a decodificar nada aquí.
"""
from django.conf import settings
from rest_framework.permissions import BasePermission
from apps.usuarios.ambitos import AMBITO_FORMAL, AMBITO_FORMATIVA


class _TieneAmbito(BasePermission):
    ambito_requerido = None
    message = "Este token no tiene acceso a este módulo."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.auth is None:
            # Solo se permite pasar sin validar ámbito cuando el flag está
            # explícitamente activado (ver config/settings/base.py, bloque
            # `if 'test' in sys.argv`). En producción este flag no existe
            # -> getattr devuelve False -> se niega el acceso, incluso si
            # llega una request autenticada por un backend distinto a JWT
            # (p. ej. SessionAuthentication).
            return getattr(settings, "AMBITO_CHECK_PERMISIVO_SIN_AUTH", False)

        return request.auth.get("ambito") == self.ambito_requerido


class TieneAmbitoFormal(_TieneAmbito):
    ambito_requerido = AMBITO_FORMAL
    message = "Este token no tiene acceso a investigación formal."


class TieneAmbitoFormativa(_TieneAmbito):
    ambito_requerido = AMBITO_FORMATIVA
    message = "Este token no tiene acceso a investigación formativa."