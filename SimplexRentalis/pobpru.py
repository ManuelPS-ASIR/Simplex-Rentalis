# pobpru.py
#python manage.py shell
#exec(open('pobpru.py').read())
import os
import django

from SimplexRentalisAPP.models import User, Property, Traveler, Booking, PropertyImage, Review, Availability, Pricing
from django.utils import timezone

def create_test_data():
    # Crear usuarios de prueba
    owner1 = User.objects.create(username='owner1', password='password123', email='owner1@example.com', user_type='owner')
    owner2 = User.objects.create(username='owner2', password='password456', email='owner2@example.com', user_type='owner')
    traveler1 = User.objects.create(username='traveler1', password='password789', email='traveler1@example.com', user_type='traveler')
    
    # Crear propiedades de prueba
    property1 = Property.objects.create(owner=owner1, title='Cabaña Acogedora', description='Una cabaña acogedora en el bosque.', location='Zona Montañosa')
    property2 = Property.objects.create(owner=owner1, title='Casa de Playa', description='Una hermosa casa de playa con vista al mar.', location='Zona Costera')
    property3 = Property.objects.create(owner=owner2, title='Apartamento en la Ciudad', description='Un apartamento en el centro de la ciudad.', location='Centro de la Ciudad')

    # Crear viajeros de prueba
    traveler1_instance = Traveler.objects.create(user=traveler1, document_type='passport', document_number='123456789', nationality='PaísA')

    # Crear reservas de prueba
    booking1 = Booking.objects.create(property=property1, traveler=traveler1_instance, check_in=timezone.now().date(), check_out=timezone.now().date())
    
    # Crear imágenes de propiedades de prueba
    PropertyImage.objects.create(property=property1, image='property_images/cottage.jpg', description='Exterior de la Cabaña')
    PropertyImage.objects.create(property=property2, image='property_images/beach_house.jpg', description='Vista de la Casa de Playa')
    
    # Crear opiniones de prueba
    review1 = Review.objects.create(property=property1, traveler=traveler1_instance, rating=5, comment='¡Lugar increíble! Lo recomiendo mucho.')
    
    # Crear disponibilidad de prueba
    Availability.objects.create(property=property1, available_date=timezone.now().date(), is_available=True)
    
    # Crear precios de prueba
    Pricing.objects.create(property=property1, price=100.00, effective_date=timezone.now().date())
    
    print("Datos de prueba creados exitosamente.")

# Llamar a la función para crear datos de prueba
create_test_data()
