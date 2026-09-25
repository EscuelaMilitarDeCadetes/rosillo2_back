from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de tus apps    
    path('api/common/', include('apps.common.urls')),
    path('api/crm/', include('apps.crm.urls')),
    path('api/integracion/', include('apps.integracion.urls')),
    path('api/institucional/', include('apps.institucional.urls')),
    path('api/investigacion-formal/', include('apps.investigacion_formal.urls')),
    path('api/investigacion-formativa/', include('apps.investigacion_formativa.urls')),
    path('api/usuarios/', include('apps.usuarios.urls')),
]