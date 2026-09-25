# apps/investigacion_formativa/selectors/certificacion_externa_selector.py
from apps.investigacion_formativa.models import CertificacionExterna


class CertificacionExternaSelector:
    @staticmethod
    def listar():
        return (
            CertificacionExterna.objects
            .select_related('proceso', 'certificado_asistencia', 'certificado_aprobacion', 'validado_por')
            .filter(activo=True)
            .order_by('-fecha_inicio')
        )

    @staticmethod
    def obtener(certificacion_id):
        return CertificacionExterna.objects.get(pk=certificacion_id)

    @staticmethod
    def listar_por_proceso(proceso_id):
        return (
            CertificacionExterna.objects
            .select_related('certificado_asistencia', 'certificado_aprobacion', 'validado_por')
            .filter(proceso_id=proceso_id, activo=True)
            .order_by('-fecha_inicio')
        )

    @staticmethod
    def listar_pendientes_validacion(proceso_id=None):
        """Certificaciones con certificado de aprobación cargado pero aún sin validar por facultades."""
        qs = CertificacionExterna.objects.filter(
            certificado_aprobacion__isnull=False, fecha_validacion__isnull=True, activo=True,
        )
        if proceso_id is not None:
            qs = qs.filter(proceso_id=proceso_id)
        return qs.order_by('fecha_inicio')