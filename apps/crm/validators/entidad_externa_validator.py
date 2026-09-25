from rest_framework.exceptions import ValidationError

TIPOS_RELACION_VALIDOS = {'FINANCIADOR', 'COOPERANTE'}


class EntidadExternaValidator:

    @staticmethod
    def validar_creacion(nombre, sector, pais, tipo_relacion):
        EntidadExternaValidator._validar_nombre(nombre)
        EntidadExternaValidator._validar_sector(sector)
        EntidadExternaValidator._validar_pais(pais)
        EntidadExternaValidator._validar_tipo_relacion(tipo_relacion)

    @staticmethod
    def validar_actualizacion(entidad_id, nombre, sector, pais, tipo_relacion):
        EntidadExternaValidator._validar_nombre(nombre)
        EntidadExternaValidator._validar_sector(sector)
        EntidadExternaValidator._validar_pais(pais)
        EntidadExternaValidator._validar_tipo_relacion(tipo_relacion)

    @staticmethod
    def validar_eliminacion(entidad_externa):
        EntidadExternaValidator._validar_sin_interacciones_asociadas(entidad_externa)

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre de la entidad externa es obligatorio."})
        if len(nombre) > 255:
            raise ValidationError(
                {"nombre": f"El nombre '{nombre}' supera el máximo de 255 caracteres."}
            )

    @staticmethod
    def _validar_sector(sector):
        if not sector or not sector.strip():
            raise ValidationError({"sector": "El sector es obligatorio."})
        if len(sector) > 100:
            raise ValidationError(
                {"sector": f"El sector '{sector}' supera el máximo de 100 caracteres."}
            )

    @staticmethod
    def _validar_pais(pais):
        if not pais or not pais.strip():
            raise ValidationError({"pais": "El país es obligatorio."})
        if len(pais) > 100:
            raise ValidationError(
                {"pais": f"El país '{pais}' supera el máximo de 100 caracteres."}
            )

    @staticmethod
    def _validar_tipo_relacion(tipo_relacion):
        if not tipo_relacion:
            raise ValidationError({"tipo_relacion": "El tipo de relación es obligatorio."})
        if tipo_relacion not in TIPOS_RELACION_VALIDOS:
            raise ValidationError(
                {"tipo_relacion": (
                    f"'{tipo_relacion}' no es un tipo de relación válido. "
                    f"Use uno de: {sorted(TIPOS_RELACION_VALIDOS)}."
                )}
            )

    @staticmethod
    def _validar_sin_interacciones_asociadas(entidad_externa):
        # Import diferido para evitar dependencia circular entre validators
        # del mismo módulo.
        from apps.crm.selectors.interaccion_selector import InteraccionSelector

        if InteraccionSelector.listar_por_entidad(entidad_externa.pk).exists():
            raise ValidationError(
                f"No se puede eliminar la entidad externa "
                f"'{entidad_externa.nombre}' (id={entidad_externa.pk}) porque "
                f"tiene interacciones registradas. Elimine primero esas "
                f"interacciones si realmente desea borrar la entidad."
            )