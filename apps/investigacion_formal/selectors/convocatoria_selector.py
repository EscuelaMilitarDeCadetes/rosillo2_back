from apps.investigacion_formal.models import Convocatoria


class ConvocatoriaSelector:

    @staticmethod
    def listar():
        return Convocatoria.objects.all().order_by('-anio_convocatoria', 'nombre_convocatoria')

    @staticmethod
    def obtener(convocatoria_id):
        return Convocatoria.objects.get(pk=convocatoria_id)

    @staticmethod
    def buscar(convocatoria_id):
        return Convocatoria.objects.filter(pk=convocatoria_id).first()

    @staticmethod
    def existe(convocatoria_id):
        return Convocatoria.objects.filter(pk=convocatoria_id).exists()

    @staticmethod
    def existe_nombre(nombre_convocatoria, excluir_id=None):
        qs = Convocatoria.objects.filter(nombre_convocatoria__iexact=nombre_convocatoria)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_internas(estado=None):
        qs = Convocatoria.objects.filter(interno=True)
        if estado is not None:
            qs = qs.filter(estado=estado)
        return qs.order_by('-anio_convocatoria')
    
    @staticmethod
    def listar_abiertas():
        return (
            Convocatoria.objects
            .filter(interno=True, estado=True)
            .order_by('-anio_convocatoria', 'cierre')
        )
    
    @staticmethod
    def buscar_por_nombre(nombre_convocatoria):
        """Variante silenciosa de obtener(): retorna None si no existe,
        en vez de lanzar excepción. Necesaria para el patrón
        buscar-o-crear de crear_proyecto_externo()."""
        return Convocatoria.objects.filter(
            nombre_convocatoria=nombre_convocatoria
        ).first()
    
    @staticmethod
    def listar_calificadas(interno):
        """
        Réplica de ConvocatoriaInternaRepositorio.getQualifiedConvocatories(interno):
        solo convocatorias que tengan al menos un proyecto con calificación
        finalizada y aprobada, del tipo (interno/externo) solicitado.
        Usado por ProyectoXConvocatoriaViewSet.opciones_filtro para poblar el
        filtro "Convocatoria" de adminProyectosExternos / proyectosAprobados /
        proyectosRechazados (a diferencia de segProyectos.html, que usa la
        lista sin filtrar `listar()`).
        """
        return (
            Convocatoria.objects
            .filter(
                proyectoxconvocatoria__estado_finalizado_calificacion=True,
                proyectoxconvocatoria__proyecto__estado_aprobado='APROBADO',
                proyectoxconvocatoria__proyecto__interno=interno,
            )
            .order_by('nombre_convocatoria')
            .distinct()
        )
 
    @staticmethod
    def listar_anios_calificadas(interno):
        """
        Réplica de ConvocatoriaInternaRepositorio.getYearsOfQualifiedConvocatories(interno):
        años de convocatoria de esas mismas convocatorias calificadas.
        """
        return (
            ConvocatoriaSelector.listar_calificadas(interno)
            .exclude(anio_convocatoria__isnull=True)
            .order_by('-anio_convocatoria')
            .values_list('anio_convocatoria', flat=True)
            .distinct()
        )