from rest_framework import serializers
from apps.investigacion_formal.models import ProyectoXConvocatoria, Monto
from apps.investigacion_formal.selectors.responsable_proyecto import etiqueta_responsable


class ProyectoXConvocatoriaSerializer(serializers.ModelSerializer):
    proyecto_titulo = serializers.CharField(source='proyecto.titulo', read_only=True)
    proyecto_codigo = serializers.CharField(source='proyecto.codigo', read_only=True)
    proyecto_fecha_inicio = serializers.DateField(source='proyecto.fecha_inicio', read_only=True)
    proyecto_financiado = serializers.BooleanField(source='proyecto.financiado', read_only=True)
    proyecto_gruplac = serializers.BooleanField(source='proyecto.gruplac', read_only=True)
    convocatoria_nombre = serializers.CharField(source='convocatoria.nombre_convocatoria', read_only=True)
    convocatoria_interno = serializers.BooleanField(source='convocatoria.interno', read_only=True)
    convocatoria_anio = serializers.IntegerField(source='convocatoria.anio_convocatoria', read_only=True)
    monto_id = serializers.SerializerMethodField()
    monto_aprobado = serializers.SerializerMethodField()
    monto_solicitado = serializers.SerializerMethodField()
    monto_contrapartida = serializers.SerializerMethodField()
    monto_total = serializers.SerializerMethodField()
    tiene_investigadores = serializers.BooleanField(read_only=True)
    tiene_productos = serializers.BooleanField(read_only=True)
    tiene_objetivos = serializers.BooleanField(read_only=True)
    responsable = serializers.SerializerMethodField()

    class Meta:
        model = ProyectoXConvocatoria
        fields = '__all__'

    def _monto(self, obj):
        """
        Punto único de acceso al Monto asociado al proyecto. Cachea el
        resultado en la propia instancia de ProyectoXConvocatoria para que
        get_monto_id/get_monto_aprobado/get_monto_solicitado, al serializar
        la misma fila, disparen UNA sola consulta en vez de tres (el
        original hacía dos consultas separadas; se agrega monto_id sin
        sumar una tercera).

        Nota de rendimiento pendiente: esto no resuelve el N1 a través de
        las FILAS de un listado paginado (20 filas = 20 consultas de Monto).
        Si se confirma que es un problema real en producción, la solución
        de fondo es un prefetch_related/Prefetch en
        ProyectoXConvocatoriaSelector.buscar_con_filtros() sobre
        'proyecto__monto_set', no un parche aquí en el serializer.
        """
        if not hasattr(obj, '_monto_cache'):
            obj._monto_cache = Monto.objects.filter(proyecto_id=obj.proyecto_id).first()
        return obj._monto_cache

    def get_monto_id(self, obj):
        monto = self._monto(obj)
        return monto.id if monto else None

    def get_monto_aprobado(self, obj):
        """
        Réplica de proyecto.montoFk.aprobado en el fragmento Thymeleaf
        modalProyectosPorConvocatoria.html. Se devuelve None cuando no hay
        monto o aún no ha sido aprobado (0/None); el frontend lo renderiza
        como 'sin aprobar', igual que hacía el th:if=... == 0 del original.
        """
        monto = self._monto(obj)
        if monto is None or not monto.aprobado:
            return None
        return monto.aprobado

    def get_monto_solicitado(self, obj):
        """Réplica de proyecto.montoFk.solicitado (columna 'Valor Solicitado')."""
        monto = self._monto(obj)
        if monto is None or not monto.solicitado:
            return None
        return monto.solicitado
    
    def get_monto_contrapartida(self, obj):
        """Réplica de proyecto.montoFk.contrapartida (columna 'Valor contrapartida')."""
        monto = self._monto(obj)
        if monto is None or not monto.contrapartida:
            return None
        return monto.contrapartida

    def get_monto_total(self, obj):
        """Réplica de proyecto.montoFk.total (columna 'Valor total')."""
        monto = self._monto(obj)
        if monto is None or not monto.total:
            return None
        return monto.total
    
    def get_responsable(self, obj):
        return etiqueta_responsable(obj.proyecto)