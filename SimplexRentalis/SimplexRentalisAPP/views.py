from django.shortcuts import render
from django.http import HttpResponse

from django.views.generic import ListView
from SimplexRentalisAPP.models import Property
# Create your views here.
class PropertyViews(ListView):
    model = Property
    context_object_name = "propietarios_de_los_hogares"


def index(request):
    return HttpResponse("Página Index de SimplesRentalisAPP")