from SimplexRentalisAPP.models import Usuarios, Propiedades, Imagenes, Opiniones, Reservas, DocumentosDeIdentidades

#python manage.py shell
#exec(open('delpobpru.py').read())
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