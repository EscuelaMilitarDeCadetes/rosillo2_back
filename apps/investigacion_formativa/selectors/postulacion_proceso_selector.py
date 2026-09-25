from apps.investigacion_formativa.models import PostulacionProceso


class PostulacionProcesoSelector:

    @staticmethod
    def listar():
        return (
            PostulacionProceso.objects
            .select_related('estudiante__persona', 'modalidad__facultad', 'modalidad__modalidad', 'proceso_creado')
            .all()
        )

    @staticmethod
    def obtener(postulacion_id):
        return (
            PostulacionProceso.objects
            .select_related('estudiante__persona', 'modalidad__facultad', 'modalidad__modalidad', 'proceso_creado')
            .get(pk=postulacion_id)
        )

    @staticmethod
    def listar_por_estudiante(estudiante_id):
        return (
            PostulacionProceso.objects
            .select_related('modalidad__facultad', 'modalidad__modalidad', 'proceso_creado')
            .filter(estudiante_id=estudiante_id)
            .order_by('-fecha_postulacion')
        )

    @staticmethod
    def existe_postulacion(estudiante_id, modalidad_id, excluir_id=None):
        qs = PostulacionProceso.objects.filter(estudiante_id=estudiante_id, modalidad_id=modalidad_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_pendientes_por_facultad(facultad_id):
        """Postulaciones ENVIADA o EN_VALIDACION cuya modalidad pertenece a la facultad dada."""
        return (
            PostulacionProceso.objects
            .select_related('estudiante__persona', 'modalidad__modalidad')
            .filter(modalidad__facultad_id=facultad_id, estado__in=['ENVIADA', 'EN_VALIDACION'])
            .order_by('fecha_postulacion')
        )
    
    @staticmethod
    def obtener_ultima_aprobada(estudiante_id):
        """Última postulación APROBADA de un estudiante (con su proceso
        creado), para decidir si puede volver a postular a otra modalidad."""
        return (
            PostulacionProceso.objects
            .filter(estudiante_id=estudiante_id, estado='APROBADA')
            .select_related('proceso_creado')
            .order_by('-fecha_decision')
            .first()
        )