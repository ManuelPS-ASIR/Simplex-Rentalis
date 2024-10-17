from django.contrib import admin

# Register your models here.
from .models import Usuarios, Propiedades, Imagenes, Opiniones, Reservas, DocumentosDeIdentidades

# Registrar cada modelo de forma individual
admin.site.register(Usuarios)
admin.site.register(Propiedades)
admin.site.register(Imagenes)
admin.site.register(Opiniones)
admin.site.register(Reservas)
admin.site.register(DocumentosDeIdentidades)