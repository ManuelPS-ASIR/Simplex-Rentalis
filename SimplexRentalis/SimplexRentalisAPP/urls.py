from django.urls import path

from . import views
from SimplexRentalisAPP.views import PropertyViews


urlpatterns = [
    path("", views.index, name="index"),
    
    path("Properties/", PropertyViews.as_view(), name='properties'),
]
