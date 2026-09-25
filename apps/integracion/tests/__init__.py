from .base import IntegracionFixturesMixin
from .test_flujos_creacion import (
    FlujoAdministrativoTests,
    FlujoFacultadTests,
    FlujoGrupoTests,
)
from .test_permisos import PermisosVinculacionTests
from .test_reemplazo_retiro import ReemplazoRetiroTests
from .test_validaciones import ValidacionesVinculacionTests
from .test_ciclo_vida_usuario import CicloVidaUsuarioTests
from .test_asignar_rol_existente import AsignarRolExistenteTests