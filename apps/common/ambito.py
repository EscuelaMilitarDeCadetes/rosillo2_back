"""
Determina el ámbito de investigación (formal/formativa) del usuario
autenticado, a partir del claim 'ambito' del JWT (ver
apps/usuarios/ambitos.py y apps/usuarios/permissions/tiene_ambito.py),
para filtrar TipoDocumento sin depender de un parámetro que el frontend
pudiera manipular.
"""
from apps.usuarios.ambitos import AMBITO_FORMAL, AMBITO_FORMATIVA

SIN_AMBITO = "__sin_ambito__"
_AMBITOS_VALIDOS = {AMBITO_FORMAL, AMBITO_FORMATIVA}


def investigacion_visible(request):
    """
    request.auth es la instancia de AccessToken ya validada por
    JWTAuthentication (soporta .get() como un dict). Si no hay claim
    'ambito' (token de otro tipo, o AMBITO_CHECK_PERMISIVO_SIN_AUTH en
    tests) se devuelve un valor que no coincide con ningún
    TipoDocumento, en vez de mostrar todo el catálogo sin filtrar.
    """
    if request.auth is None:
        return SIN_AMBITO
    ambito = request.auth.get("ambito")
    return ambito if ambito in _AMBITOS_VALIDOS else SIN_AMBITO