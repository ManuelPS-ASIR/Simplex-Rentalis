# # SimplexRentalisAPP/views.py
from django.shortcuts import render#, get_object_or_404
# from django.http import HttpResponse
# from django.views.generic import View, ListView, DetailView
from .models import Propiedades  # Asegúrate de usar los nombres correctos

# # Create your views here.
# class Probando(View):
#     def get(self, request):
#         return render(request, 'SimplexRentalisAPP/probandohtml.html')


# class PropiedadesListView(ListView):
#     model = Propiedades
#     template_name = 'SimplexRentalisAPP/propiedades_list.html'
#     context_object_name = 'propiedades'  # Cambia esto para que sea más legible

#     def get_queryset(self):
#         return Propiedades.objects.all()  # Filtra o retorna todas las propiedades

#     def get_context_data(self, **kwargs):
#         # Llama a la implementación del contexto padre
#         context = super().get_context_data(**kwargs)

#         # Añade la imagen de portada a cada propiedad
#         for propiedad in context['propiedades']:
#             propiedad.imagen_portada = propiedad.obtener_imagen_portada()  # Accede al método del modelo

#         return context


# class PropiedadDetailView(DetailView):
#     model = Propiedades
#     template_name = 'SimplexRentalisAPP/propiedad_detallada.html'  # La plantilla que usarás para mostrar los detalles
#     context_object_name = 'propiedad'  # Este será el nombre en el contexto

#     def get_context_data(self, **kwargs):
#         # Llama a la implementación del contexto padre
#         context = super().get_context_data(**kwargs)
#         # Obtiene la propiedad actual
#         propiedad = self.object
#         # Obtiene la imagen portada
#         imagen_portada = propiedad.imagenes_set.filter(es_portada=True).first()
#         # Añade la imagen de portada al contexto
#         context['imagen_portada'] = imagen_portada
#         return context


# def detalle_propiedad(request, propiedad_id):
#     propiedad = get_object_or_404(Propiedades, id=propiedad_id)

#     # Obtiene la imagen de portada utilizando la relación inversa
#     imagen_portada = propiedad.imagenes_set.filter(es_portada=True).first()  # Cambia 'visual' a 'imagenes_set'
    
#     # Obtiene todas las imágenes de la propiedad
#     imagenes = propiedad.imagenes_set.all()  # Esto obtendrá todas las imágenes relacionadas con la propiedad

#     return render(request, 'detalle_propiedad.html', {
#         'propiedad': propiedad,
#         'imagen_portada': imagen_portada,
#         'imagenes': imagenes  # Agrega esta línea para pasar todas las imágenes
#     })


def index(request):
    # Filtrar propiedades según el criterio que elijas
    propiedades_mas_visitadas = Propiedades.objects.filter(visitas__gte=10)  # Cambia a otro campo si es necesario
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })
