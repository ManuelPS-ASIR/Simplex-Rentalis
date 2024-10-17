# SimplexRentalisAPP/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View  # Importa la clase View
from django.views.generic import ListView
from SimplexRentalisAPP.models import Usuario, Propiedad  # Asegúrate de usar los nombres correctos

# Create your views here.

class PropiedadesViews(View):
    def get(self, request):
        propiedades = Propiedad.objects.all()  # Obtener todas las propiedades
        return render(request, 'SimplexRentalisAPP/propiedades_list.html', {'propiedades': propiedades})  # Asegúrate de que esta plantilla exista


def index(request):
    # Filtrar propiedades según el criterio que elijas
    propiedades_mas_visitadas = Propiedad.objects.filter(visitas__gte=10)  # Cambia a otro campo si es necesario
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })
