from rest_framework import serializers
from apps.usuarios.models import RolXUsuario


class RolXUsuarioSerializer(serializers.ModelSerializer):
    """
    Réplica de la tabla "Usuarios Activos registrados" de usuarios.html,
    cuya fuente original era RolXUsuarioRepositorio.getDatosPersonasSinGrupo():
        rol_x_usuario -> usuario -> persona -> grado_estudios (INNER JOINs).

    RolXUsuario se mantiene como raíz -> se enriquece este serializer en vez
    de migrar la tabla a UsuarioXPersonaViewSet, que invertiría la entidad
    base (de "roles activos, con su persona" a "asignaciones persona-usuario,
    con su rol resuelto lateralmente") frente al diseño original.

    El join original usaba `usuario.persona_fk` (FK directa). En el modelo
    actual esa relación está historizada vía UsuarioXPersona
    (usuario.asignaciones, filtrando estado=True para la asignación
    vigente) — mismo patrón que UsuarioSerializer._persona_actual().
    """
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    usuario_is_active = serializers.BooleanField(source='usuario.is_active', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre_rol', read_only=True)

    persona_grado = serializers.SerializerMethodField()
    persona_nombre = serializers.SerializerMethodField()
    persona_apellido = serializers.SerializerMethodField()
    persona_documento = serializers.SerializerMethodField()
    persona_celular = serializers.SerializerMethodField()
    persona_correo = serializers.SerializerMethodField()

    class Meta:
        model = RolXUsuario
        fields = '__all__'

    def _persona_actual(self, obj):
        # obj.usuario.asignaciones ya viene prefetcheado con estado=True
        # desde RolXUsuarioViewSet.get_queryset() -> no dispara N+1 por fila.
        asignaciones = list(obj.usuario.asignaciones.all())
        return asignaciones[0].persona if asignaciones else None

    def get_persona_grado(self, obj):
        persona = self._persona_actual(obj)
        # sigla_grado, no descripcion completa, para respetar la columna
        # "Grado" del original (mostraba p.gradoFk.sigla).
        return persona.grado.sigla_grado if persona else None

    def get_persona_nombre(self, obj):
        persona = self._persona_actual(obj)
        return persona.nombre if persona else None

    def get_persona_apellido(self, obj):
        persona = self._persona_actual(obj)
        return persona.apellido if persona else None

    def get_persona_documento(self, obj):
        persona = self._persona_actual(obj)
        return persona.documento if persona else None

    def get_persona_celular(self, obj):
        persona = self._persona_actual(obj)
        return persona.celular if persona else None

    def get_persona_correo(self, obj):
        persona = self._persona_actual(obj)
        return persona.correo if persona else None