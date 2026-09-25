# Estructura de módulos

Exceptuando el modulo de usuarios cada módulo Django sigue la estructura de forma general:

apps/modulo/

migrations/
models/
selectors/
serializers/
services/
tests/
validators/
views/
admin.py
apps.py
pagination.py
urls.py


# Modulo usuarios
Tiene la siguiente estructura

migrations/
models/
permissions/
serializers/
services/
tests/
views/
admin.py
ambitos.py
apps.py
constants.py
pagination.py
throttles.py
urls.py


# Modulo integracion
Tiene la siguiente excepción
sin admin.py


# Modulo common
Tiene las siguientes excepciones, adicionales:
consumers.py
middleware_ws.py
routing.py
signals.py
tasks.py

# Modulo investigacion_formal
Tiene la siguiente excepción, adicionales:
permissions.py (archivo unico, no paquete: reutiliza y combina los roles ya definidos en usuarios/permissions via un helper combinar())

# Modulo investigacion_formativa
Tiene la siguiente excepción, adicionales:
permissions.py (archivo unico, no paquete: reutiliza y combina los roles ya definidos en usuarios/permissions via un helper combinar())