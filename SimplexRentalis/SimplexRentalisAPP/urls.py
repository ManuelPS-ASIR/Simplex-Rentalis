from django.urls import path
from . import views
from SimplexRentalisAPP.views import PropiedadesViews
#from SimplexRentalisAPP.views import UserDataView



urlpatterns = [
    path("", views.index, name="index"),
    path("propiedades/", views.PropiedadesViews.as_view(), name="propiedades"),  # Asegúrate de que esto exista
]