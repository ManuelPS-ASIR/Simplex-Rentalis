from SimplexRentalisAPP.models import User, Property, Traveler, Booking, PropertyImage, Review, Availability, Pricing
#python manage.py shell
#exec(open('delpobpru.py').read())
# Delete all test users
User.objects.filter(username__in=['owner1', 'owner2', 'traveler1']).delete()

# Delete all properties
Property.objects.all().delete()

# Delete all travelers
Traveler.objects.all().delete()

# Delete all bookings
Booking.objects.all().delete()

# Delete all property images
PropertyImage.objects.all().delete()

# Delete all reviews
Review.objects.all().delete()

# Delete all availabilities
Availability.objects.all().delete()

# Delete all pricing entries
Pricing.objects.all().delete()