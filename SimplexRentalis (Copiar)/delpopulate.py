from SimplexRentalisAPP.models import Usuarios, Propiedades, Imagenes, Opiniones, Reservas, DocumentosDeIdentidades

#python manage.py shell
#exec(open('delpopulate.py').read())
# Delete all test users
Usuarios.objects.all().delete()

# Delete all properties
Propiedades.objects.all().delete()

# Delete all travelers
Imagenes.objects.all().delete()

# Delete all bookings
Opiniones.objects.all().delete()

# Delete all property images
Reservas.objects.all().delete()

# Delete all reviews
DocumentosDeIdentidades.objects.all().delete()
# (WorkDjango) manu@manu-pavilion:~/Escritorio/AppWebJavi/SimplexRentalis$ python3 manage.py shell
# Python 3.12.3 (main, Sep 11 2024, 14:17:37) [GCC 13.2.0] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# (InteractiveConsole)
# >>> Usuarios.objects.all().delete()
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# NameError: name 'Usuarios' is not defined
# >>> Usuarios.objects.all().delete()
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# NameError: name 'Usuarios' is not defined
# >>> Usuarios.objects.all().delete()
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# NameError: name 'Usuarios' is not defined
# >>> from SimplexRentalisAPP.models import Usuarios, Propiedades, Imagenes, Opiniones, Reservas, DocumentosDeIdentidades
# >>> Usuarios.objects.all().delete()
# (0, {})
# >>> Propiedades.objects.all().delete()
# (0, {})
# >>> Imagenes.objects.all().delete()
# (0, {})
# >>> 
# >>> Opiniones.objects.all().delete()
# (0, {})
# >>> Reservas.objects.all().delete()
# (0, {})
# >>> DocumentosDeIdentidades.objects.all().delete()
# (0, {})
# >>> from SimplexRentalisAPP.models import Usuarios, Propiedades, Imagenes, Opiniones, Reservas, DocumentosDeIdentidades
# >>> from django.utils import timezone
# >>> usuario1 = Usuarios.objects.create(nombre='Juan Pérez', correo='juan@example.com', contrasena='password123', es_propietario=True)
# >>> usuario2 = Usuarios.objects.create(nombre='Ana García', correo='ana@example.com', contrasena='password123', es_propietario=False)
# >>> propiedad1 = Propiedades.objects.create(usuario=usuario1, titulo='Apartamento en el centro', direccion='Calle Mayor 123', descripcion='Amplio apartamento en el centro de la ciudad', precio=100.00, calificacion=4.5, porcentaje_reserva=50.0)
# >>> propiedad2 = Propiedades.objects.create(usuario=usuario1, titulo='Casa de campo', direccion='Camino del bosque 456', descripcion='Casa de campo con vistas', precio=150.00, calificacion=4.8, porcentaje_reserva=70.0)
# >>> propiedad3 = Propiedades.objects.create(usuario=usuario2, titulo='Estudio en la playa', direccion='Playa del sol 789', descripcion='Estudio con acceso a la playa', precio=80.00, calificacion=4.2, porcentaje_reserva=30.0)
# >>> imagen1 = Imagenes.objects.create(propiedad=propiedad1, imagen='imagenes/apartamento_centro.jpg', es_portada=True)
# >>> imagen2 = Imagenes.objects.create(propiedad=propiedad2, imagen='imagenes/casa_campo.jpg', es_portada=True)
# >>> imagen3 = Imagenes.objects.create(propiedad=propiedad3, imagen='imagenes/estudio_playa.jpg', es_portada=True)
# >>> opinion1 = Opiniones.objects.create(propiedad=propiedad1, usuario=usuario2, puntuacion=5, comentario='Excelente lugar, muy recomendado!')
# >>> opinion2 = Opiniones.objects.create(propiedad=propiedad2, usuario=usuario1, puntuacion=4, comentario='Bonita casa, pero algo alejada del centro.')
# >>> reserva1 = Reservas.objects.create(usuario=usuario2, propiedad=propiedad1, fecha_entrada=timezone.now().date(), fecha_salida=timezone.now().date(), adultos=2, ninos=0, mascotas=False, tipo_mascota=None, precio_noche=100.00)
# >>> reserva2 = Reservas.objects.create(usuario=usuario1, propiedad=propiedad3, fecha_entrada=timezone.now().date(), fecha_salida=timezone.now().date(), adultos=1, ninos=1, mascotas=True, tipo_mascota='perro', precio_noche=80.00)
# >>> documento1 = DocumentosDeIdentidades.objects.create(reserva=reserva1, tipo_documento='DNI', numero_documento='12345678A', fecha_expedicion='2020-01-01', primer_apellido='Pérez', segundo_apellido='López', nombre='Juan', sexo='masculino', fecha_nacimiento='1990-05-15', pais_nacionalidad='España', fecha_entrada='2024-10-01')
# >>> documento2 = DocumentosDeIdentidades.objects.create(reserva=reserva2, tipo_documento='Pasaporte', numero_documento='A1234567', fecha_expedicion='2023-01-01', primer_apellido='García', segundo_apellido='Martínez', nombre='Ana', sexo='femenino', fecha_nacimiento='1988-03-20', pais_nacionalidad='España', fecha_entrada='2024-10-01')
