from django.db import transaction
from apps.investigacion_formal.services.proyecto_setup_service import ProyectoSetupService
from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.models import ProductoXProyecto
from apps.investigacion_formal.selectors.producto_x_proyecto_selector import (
    ProductoXProyectoSelector,
)
from apps.investigacion_formal.validators.producto_x_proyecto_validator import (
    ProductoXProyectoValidator,
)
from apps.common.services.historial_service import HistorialService
from apps.common.services.documento_firma_service import DocumentoFirmaService
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector


class ProductoXProyectoService:

    # Tipo de documento fijo para toda entrega de producto: el usuario nunca
    # lo elige (a diferencia de participar_convocatoria, que sí deja elegir
    # entre "Propuesta del proyecto"/"Carta de Compromiso"/"Documento de
    # Alianza"). Se resuelve por nombre, no por pk fijo, para no depender del
    # orden en que se corrieron los seeds en cada entorno.
    NOMBRE_TIPO_DOCUMENTO_ENTREGABLE = "Entregables"

    @staticmethod
    def listar():
        return ProductoXProyectoSelector.listar()

    @staticmethod
    def obtener(producto_x_proyecto_id):
        return ProductoXProyectoSelector.obtener(producto_x_proyecto_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        return ProductoXProyectoSelector.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)

    @staticmethod
    def listar_pendientes_por_proyecto(proyecto_id):
        return ProductoXProyectoSelector.listar_pendientes_por_proyecto(proyecto_id)

    @staticmethod
    def listar_entregados_por_proyecto(proyecto_id):
        return ProductoXProyectoSelector.listar_entregados_por_proyecto(proyecto_id)

    @staticmethod
    @transaction.atomic
    def crear(producto_x_grupo_id, proyecto_id, categoria, puntaje, ejecutor):
        """Réplica de agregarProductoXProyecto: registra la producción
        prometida/esperada, aún sin entregar."""
        ProductoXProyectoValidator.validar_creacion(
            producto_x_grupo_id, proyecto_id, categoria, puntaje
        )
        producto = ProductoXProyecto.objects.create(
            producto_x_grupo_id=producto_x_grupo_id,
            proyecto_id=proyecto_id,
            categoria=categoria.strip(),
            puntaje=puntaje,
            activo=True,
            entregado=False,
            gruplac=False,
        )
        ProyectoSetupService.verificar_configuracion_completa(producto.proyecto_id, ejecutor=ejecutor)
        HistorialService.registrar(
            ejecutor,
            f"Se asignó el producto "
            f"'{producto.producto_x_grupo.producto_minciencias.nombre_producto}' "
            f"al proyecto '{producto.proyecto.titulo}' (id={producto.pk}).",
            objeto=producto,
        )
        return producto

    @staticmethod
    @transaction.atomic
    def registrar_entrega(producto_x_proyecto_id, archivo, ip_creacion, ejecutor):
        """Réplica de cargarDocumentoProducto: marca el producto como
        entregado y sube el archivo del entregable a través del punto de
        entrada único DocumentoFirmaService.crear_desde_archivo(), en la
        misma carpeta ('proyectos') que la propuesta del proyecto y la carta
        de compromiso. El tipo de documento es siempre 'Entregables' (no lo
        elige el usuario) y el documento se crea directamente en estado
        'FIRMADO' porque no pasa por ningún flujo de firmas dentro de la
        plataforma."""
        producto = ProductoXProyectoSelector.obtener(producto_x_proyecto_id)
        ProductoXProyectoValidator.validar_entrega(archivo)

        tipo_documento = TipoDocumentoSelector.obtener_por_nombre(
            ProductoXProyectoService.NOMBRE_TIPO_DOCUMENTO_ENTREGABLE
        )
        if tipo_documento is None:
            raise ValidationError(
                f"No existe el TipoDocumento "
                f"'{ProductoXProyectoService.NOMBRE_TIPO_DOCUMENTO_ENTREGABLE}' "
                f"(seed pendiente: nombre_documento="
                f"'{ProductoXProyectoService.NOMBRE_TIPO_DOCUMENTO_ENTREGABLE}')."
            )

        DocumentoFirmaService.crear_desde_archivo(
            tipo_documento_id=tipo_documento.pk,
            archivo=archivo,
            ip_creacion=ip_creacion,
            ejecutor=ejecutor,
            objeto=producto,
            estado='FIRMADO',
            carpeta='proyectos',
        )

        producto.entregado = True
        producto.save(update_fields=['entregado'])

        HistorialService.registrar(
            ejecutor,
            f"Se registró la entrega del producto "
            f"'{producto.producto_x_grupo.producto_minciencias.nombre_producto}' "
            f"del proyecto '{producto.proyecto.titulo}' (id={producto.pk}).",
            objeto=producto,
        )
        return producto

    @staticmethod
    @transaction.atomic
    def subir_a_gruplac(producto_x_proyecto_id, ejecutor):
        producto = ProductoXProyectoSelector.obtener(producto_x_proyecto_id)
        producto.gruplac = True
        producto.save(update_fields=['gruplac'])
        HistorialService.registrar(
            ejecutor,
            f"Se cargó al GrupLAC el producto "
            f"'{producto.producto_x_grupo.producto_minciencias.nombre_producto}' "
            f"del proyecto '{producto.proyecto.titulo}' (id={producto.pk}).",
            objeto=producto,
        )
        return producto

    @staticmethod
    @transaction.atomic
    def actualizar(producto_x_proyecto_id, ejecutor, categoria=None, puntaje=None):
        producto = ProductoXProyectoSelector.obtener(producto_x_proyecto_id)

        nueva_categoria = categoria if categoria is not None else producto.categoria
        nuevo_puntaje = puntaje if puntaje is not None else producto.puntaje

        ProductoXProyectoValidator.validar_actualizacion(
            producto_x_proyecto_id,
            producto.producto_x_grupo_id,
            producto.proyecto_id,
            nueva_categoria,
            nuevo_puntaje,
        )

        producto.categoria = nueva_categoria.strip()
        producto.puntaje = nuevo_puntaje
        producto.save(update_fields=['categoria', 'puntaje'])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el producto id={producto.pk} del proyecto "
            f"'{producto.proyecto.titulo}'.",
            objeto=producto,
        )
        return producto

    @staticmethod
    @transaction.atomic
    def eliminar(producto_x_proyecto_id, ejecutor):
        producto = ProductoXProyectoSelector.obtener(producto_x_proyecto_id)
        ProductoXProyectoValidator.validar_eliminacion(producto)
        producto.activo = False
        producto.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó el producto "
            f"'{producto.producto_x_grupo.producto_minciencias.nombre_producto}' "
            f"del proyecto '{producto.proyecto.titulo}' (id={producto.pk}).",
            objeto=producto,
        )
        return producto