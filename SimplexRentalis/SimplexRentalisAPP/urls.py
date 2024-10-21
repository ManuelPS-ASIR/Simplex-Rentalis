from django.urls import path
from . import views
from SimplexRentalisAPP.views import PropiedadesListView,Probando

#from SimplexRentalisAPP.views import UserDataView



urlpatterns = [
    path("", views.index, name="index"),
    path("propiedad_detallada/", PropiedadesListView.as_view(), name="propiedad_detallada"),  # Asegúrate de que esto exista
    path("propiedades/", PropiedadesListView.as_view(), name="propiedades"),  # Asegúrate de que esto exista
    path("probando/", Probando.as_view(), name="probando"),  # Asegúrate de que esto exista

]