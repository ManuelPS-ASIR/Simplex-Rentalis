from django.urls import path

from . import views
from SimplexRentalisAPP.views import PropertyViews
from SimplexRentalisAPP.views import UserDataView



urlpatterns = [
    path("", views.index, name="index"),
    
    path("Properties/", PropertyViews.as_view(), name='properties'),
    path("User/", UserDataView.as_view(), name='user'),
    path("User/<str:username>/", UserDataView.as_view(), name="user_data"),  # Ruta para capturar el username

]
