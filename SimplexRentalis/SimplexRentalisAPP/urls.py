from django.urls import path
from . import views
from SimplexRentalisAPP.views import PropiedadesListView

#from SimplexRentalisAPP.views import UserDataView



urlpatterns = [
    path("", views.index, name="index"),
    path("propiedades/", PropiedadesListView.as_view(), name="propiedades"),  # Asegúrate de que esto exista
]