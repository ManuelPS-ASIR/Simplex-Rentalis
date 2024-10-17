from SimplexRentalisAPP.models import Usuario, Propiedad, Imagen, Opinion, Reserva, DocumentoIdentidad

#python manage.py shell
#exec(open('delpobpru.py').read())
# Delete all test users
Usuario.objects.filter(username__in=['owner1', 'owner2', 'traveler1']).delete()

# Delete all properties
Propiedad.objects.all().delete()

# Delete all travelers
Imagen.objects.all().delete()

# Delete all bookings
Opinion.objects.all().delete()

# Delete all property images
Reserva.objects.all().delete()

# Delete all reviews
DocumentoIdentidad.objects.all().delete()