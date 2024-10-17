from django.contrib import admin

# Register your models here.
from .models import Usuario, Propiedad, Imagen, Opinion, Reserva, DocumentoIdentidad

# Registrar cada modelo de forma individual
admin.site.register(Usuario)
admin.site.register(Propiedad)
admin.site.register(Imagen)
admin.site.register(Opinion)
admin.site.register(Reserva)
admin.site.register(DocumentoIdentidad)