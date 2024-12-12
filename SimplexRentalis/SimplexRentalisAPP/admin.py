from django.contrib import admin

# Register your models here.
from .models import User, Propiedades, ReservaPersona, Reservas, IdentidadReserva, Opiniones, IdentidadUsuario
admin.site.register(User)
admin.site.register(Propiedades)
admin.site.register(ReservaPersona)
admin.site.register(Reservas)
admin.site.register(IdentidadReserva)
admin.site.register(IdentidadUsuario)
admin.site.register(Opiniones)
