from django.contrib import admin

# Register your models here.
from .models import User, Propiedades, ReservaPersona, Reservas, Identidades, Opiniones
admin.site.register(User)
admin.site.register(Propiedades)
admin.site.register(ReservaPersona)
admin.site.register(Reservas)
admin.site.register(Identidades)
admin.site.register(Opiniones)
