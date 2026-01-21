"""
URL configuration for cv_profesional project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Curriculum App
    path('', include('curriculum.urls')),
    
    # Markdownx (para descripciones rich text)
    path('markdownx/', include('markdownx.urls')),
]

# Configuración del Admin
admin.site.site_header = "CV Profesional - Administración"
admin.site.site_title = "CV Profesional Admin"
admin.site.index_title = "Panel de Administración"

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Handler de errores personalizados (opcional)
handler404 = 'curriculum.views.error_404'
handler500 = 'curriculum.views.error_500'
handler403 = 'curriculum.views.error_403'
