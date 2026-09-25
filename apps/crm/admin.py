from django.contrib import admin
from .models import (    
    EntidadExterna,
    IndicadorImpacto,
    Interaccion,
)


# ==============================
# ENTIDAD EXTERNA
# ==============================
@admin.register(EntidadExterna)
class EntidadExternaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'sector', 'pais')
    search_fields = ('nombre', 'sector', 'pais')
    ordering = ('nombre',)

# ==============================
# INDICADOR IMPACTO
# ==============================
@admin.register(IndicadorImpacto)
class IndicadorImpactoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proyecto__titulo', 'kpi_nombre')
    search_fields = ('proyecto__titulo', 'kpi_nombre')
    ordering = ('proyecto__titulo',)

# ==============================
# INTERACCION
# ==============================
@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'medio', 'fecha')
    search_fields = ('medio', 'fecha')
    ordering = ('medio',)