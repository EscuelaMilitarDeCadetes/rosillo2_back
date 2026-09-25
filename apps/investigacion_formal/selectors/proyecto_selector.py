from apps.investigacion_formal.models import Proyecto


class ProyectoSelector:

    @staticmethod
    def listar():
        return Proyecto.objects.select_related('usuario', 'gerente').all()

    @staticmethod
    def obtener(proyecto_id):
        return Proyecto.objects.select_related('usuario', 'gerente').get(pk=proyecto_id)

    @staticmethod
    def existe(proyecto_id):
        return Proyecto.objects.filter(pk=proyecto_id).exists()

    @staticmethod
    def existe_titulo(titulo, excluir_id=None):
        qs = Proyecto.objects.filter(titulo__iexact=titulo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_activos():
        return Proyecto.objects.select_related('usuario', 'gerente').filter(estado=True)

    @staticmethod
    def listar_por_estado_aprobado(estado_aprobado):
        """estado_aprobado: 'SIN_CALIFICAR' | 'APROBADO' | 'NO_APROBADO'."""
        return (
            Proyecto.objects
            .select_related('usuario', 'gerente')
            .filter(estado_aprobado=estado_aprobado)
        )

    @staticmethod
    def listar_anios_inicio_distintos():
        return (
            Proyecto.objects
            .filter(fecha_inicio__isnull=False)
            .dates('fecha_inicio', 'year', order='DESC')
        )

    @staticmethod
    def listar_anios_fin_distintos():
        return (
            Proyecto.objects
            .filter(fecha_fin__isnull=False)
            .dates('fecha_fin', 'year', order='DESC')
        )

    @staticmethod
    def _base_proyectos_calificados(interno=True):
        return Proyecto.objects.filter(
            interno=interno,
            estado_aprobado='APROBADO',
            proyectoxconvocatoria__estado_finalizado_calificacion=True,
        ).distinct()

    @staticmethod
    def listar_anios_inicio_proyectos_calificados(interno=True):
        return (
            ProyectoSelector._base_proyectos_calificados(interno)
            .filter(fecha_inicio__isnull=False)
            .dates('fecha_inicio', 'year', order='DESC')
        )

    @staticmethod
    def listar_anios_fin_proyectos_calificados(interno=True):
        return (
            ProyectoSelector._base_proyectos_calificados(interno)
            .filter(fecha_fin__isnull=False)
            .dates('fecha_fin', 'year', order='DESC')
        )
    
    @staticmethod
    def contar_aprobados_por_prefijo(prefijo):
        """
        Cuenta proyectos APROBADO cuyo código empieza exactamente por `prefijo`
        (p.ej. 'ING2024-I'), para calcular el consecutivo de dos dígitos.
        OJO: aquí sí es correcto usar codigo__startswith porque `prefijo` es
        literal, no un patrón LIKE con comodines.
        """
        return Proyecto.objects.filter(
            codigo__startswith=prefijo, estado_aprobado='APROBADO'
        ).count()

    @staticmethod
    def existe_codigo(codigo, excluir_id=None):
        qs = Proyecto.objects.filter(codigo=codigo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
    
    @staticmethod
    def tiene_acta_inicio(proyecto_id):
        from django.contrib.contenttypes.models import ContentType
        from apps.common.models import DocumentoFirma
        from apps.investigacion_formal.models import Proyecto

        content_type = ContentType.objects.get_for_model(Proyecto)
        return DocumentoFirma.objects.filter(
            content_type=content_type,
            object_id=proyecto_id,
            tipo_documento__es_acta_inicio=True,
        ).exists()