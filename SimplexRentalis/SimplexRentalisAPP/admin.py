from django.contrib import admin

# Register your models here.
from .models import User, Property, Traveler, Booking, Review, Availability, Pricing, ReviewImage

# Registrar cada modelo de forma individual
admin.site.register(User)
admin.site.register(Property)
admin.site.register(Traveler)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Availability)
admin.site.register(Pricing)
admin.site.register(ReviewImage)