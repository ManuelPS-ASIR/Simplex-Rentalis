from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView
from SimplexRentalisAPP.models import Usuario, Propiedad  # Asegúrate de usar los nombres correctos

# Create your views here.

class PropertyViews(ListView):
    model = Propiedad  # Usa 'Propiedad' en lugar de 'Property'
    context_object_name = "propietarios_de_los_hogares"
    queryset = Propiedad.objects.all()
    template_name = "SimplexRentalisAPP/property_list.html"  # Asegúrate de que esta plantilla exista

class UserDataView(ListView):
    template_name = "SimplexRentalisAPP/user_data.html"  # Ruta de la plantilla

    def get_queryset(self):
        # Captura el username de la URL
        self.user = get_object_or_404(Usuario, username=self.kwargs["username"])  # Usa 'Usuario'
        # Filtra las propiedades por el usuario
        return Propiedad.objects.filter(propietario=self.user)  # Usa 'propietario'

    def get_context_data(self, **kwargs):
        # Llama a la implementación base para obtener un contexto
        context = super().get_context_data(**kwargs)
        # Añade el usuario al contexto para usarlo en la plantilla
        context["usuario"] = self.user
        return context

def index(request):
    return HttpResponse("Página Index de SimplesRentalisAPP")