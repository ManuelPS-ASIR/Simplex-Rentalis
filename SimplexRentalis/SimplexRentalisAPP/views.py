# SimplexRentalisAPP/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import View,ListView, DetailView
from .models import Usuarios, Propiedades  # Asegúrate de usar los nombres correctos

# Create your views here.
class PropiedadesListView(ListView):
    model = Propiedades
    template_name = 'SimplexRentalisAPP/propiedades_list.html'
    context_object_name = 'propiedades'  # Cambia esto para que sea más legible

    def get_queryset(self):
        return Propiedades.objects.all()  # Filtra o retorna todas las propiedades



# class PropiedadesUsuarioListView(ListView):
#     model = Propiedad
#     template_name = 'SimplexRentalisAPP/propiedades_usuario_list.html'  # Asegúrate de tener esta plantilla
#     context_object_name = 'propiedades4usuario'

#     def get_queryset(self):
#         # Filtra las propiedades por el usuario que está en la URL o en la sesión.
#         usuario_id = self.kwargs['usuario_id']  # Asume que pasas el ID del usuario en la URL
#         return Propiedad.objects.filter(usuario__id=usuario_id)  # Filtra las propiedades por el usuario


def index(request):
    # Filtrar propiedades según el criterio que elijas
    propiedades_mas_visitadas = Propiedades.objects.filter(visitas__gte=10)  # Cambia a otro campo si es necesario
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })
