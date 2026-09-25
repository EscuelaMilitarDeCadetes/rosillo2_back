from apps.investigacion_formal.models import RolInvestigador


class RolInvestigadorSelector:

    @staticmethod
    def listar():
        return RolInvestigador.objects.all().order_by('nombre_rol_investigador')

    @staticmethod
    def obtener(rol_investigador_id):
        return RolInvestigador.objects.get(pk=rol_investigador_id)

    @staticmethod
    def existe(rol_investigador_id):
        return RolInvestigador.objects.filter(pk=rol_investigador_id).exists()

    @staticmethod
    def existe_nombre(nombre_rol_investigador, excluir_id=None):
        qs = RolInvestigador.objects.filter(
            nombre_rol_investigador__iexact=nombre_rol_investigador
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()