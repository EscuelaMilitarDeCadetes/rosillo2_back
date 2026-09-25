# apps/common/tests/base.py
import shutil
import tempfile
from pathlib import Path

from apps.usuarios.models import Usuario
from apps.institucional.models import FacultadEscuela
from apps.common.models import TipoDocumento


class CommonFixturesMixin:

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        self.otro_usuario = Usuario.objects.create_user(
            username='revisor@esmic.edu.co',
            email='revisor@esmic.edu.co',
            password='revisor123',
        )
        self.tipo_documento = TipoDocumento.objects.create(
            nombre_documento='Acta de Cierre', grupo='proyecto'
        )
        self.objeto_generico = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Pruebas', abreviatura='FPRB'
        )

        # Directorio temporal para simular documentos físicos en disco,
        # requerido por DocumentoFirmaService.crear() para el hash de no-repudio.
        self._tmp_dir = Path(tempfile.mkdtemp(prefix="rosillo_docs_"))

        super().setUp()

    def tearDown(self):
        shutil.rmtree(self._tmp_dir, ignore_errors=True)
        super().tearDown()

    def _crear_objeto_generico(self, nombre='Facultad Adicional', abreviatura='FADI'):
        return FacultadEscuela.objects.create(
            nombre_facultad=nombre, abreviatura=abreviatura
        )

    def _crear_archivo_temporal(self, nombre, contenido=b'contenido de prueba'):
        """
        Crea un archivo físico real dentro del directorio temporal de la
        suite y devuelve su ruta absoluta como string, lista para usarse
        como `ruta_documento` en DocumentoFirmaService.crear().
        """
        ruta = self._tmp_dir / nombre
        ruta.write_bytes(contenido)
        return str(ruta)