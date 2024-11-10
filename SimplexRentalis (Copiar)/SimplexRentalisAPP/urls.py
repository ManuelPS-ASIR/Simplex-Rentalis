#from django.conf import settings
#from django.conf.urls.static import static
from django.urls import path
from . import views
#from SimplexRentalisAPP.views import PropiedadesListView, Probando, PropiedadDetailView

urlpatterns = [
    path("", views.index, name="index"),
    # path("mis_propiedades/", PropiedadesListView.as_view(), name="mis_propiedades"),
    # path("propiedades/", PropiedadesListView.as_view(), name="propiedades"),
    # path('propiedad/<int:pk>/', PropiedadDetailView.as_view(), name='detalle_propiedad'),
    # path("probando/", Probando.as_view(), name="probando"),
]

# # Añade esta línea para servir archivos multimedia en modo DEBUG
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)