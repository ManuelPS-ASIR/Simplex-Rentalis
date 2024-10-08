from django.db import models

# Tabla para los usuarios (Propietarios y Viajeros)
class User(models.Model):
    # Lista de opciones para el tipo de usuario (propietario o viajero)
    USER_TYPE_CHOICES = [
        ('traveler', 'Traveler'),  # Opción viajero
        ('owner', 'Owner'),        # Opción propietario
    ]
    
    # Campo de nombre de usuario, debe ser único y no mayor a 50 caracteres
    username = models.CharField(max_length=50, unique=True)
    # Campo de contraseña, en formato de texto largo (encriptada en general)
    password = models.CharField(max_length=255)
    # Campo de correo electrónico, debe ser único y no mayor a 100 caracteres
    email = models.EmailField(max_length=100, unique=True)
    # Campo que almacena el tipo de usuario (traveler o owner)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    # Campo de fecha de creación del usuario, se asigna automáticamente al crear
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra el nombre de usuario
    def __str__(self):
        return self.username


# Tabla para las propiedades
class Property(models.Model):
    # Relación con el usuario propietario, elimina la propiedad si el usuario es eliminado
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # Campo de título de la propiedad, no mayor a 100 caracteres
    title = models.CharField(max_length=100)
    # Campo de descripción opcional de la propiedad
    description = models.TextField(blank=True, null=True)
    # Campo de localización de la propiedad
    location = models.CharField(max_length=255)
    # Fecha de creación de la propiedad, se asigna automáticamente al crearla
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra el título de la propiedad
    def __str__(self):
        return self.title


# Tabla para los viajeros
class Traveler(models.Model):
    # Lista de opciones para el tipo de documento del viajero (pasaporte o ID nacional)
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Passport'),         # Opción pasaporte
        ('national_id', 'National ID'),   # Opción ID nacional
    ]
    
    # Relación con el usuario, un viajero es un tipo de usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Campo para el tipo de documento, se selecciona entre las opciones definidas
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    # Número del documento, debe ser único y no mayor a 50 caracteres
    document_number = models.CharField(max_length=50, unique=True)
    # Campo opcional de nacionalidad
    nationality = models.CharField(max_length=50, blank=True, null=True)

    # Representación del objeto como una cadena, muestra el número del documento
    def __str__(self):
        return self.document_number


# Tabla para las reservas
class Booking(models.Model):
    # Relación con la propiedad reservada, elimina la reserva si se elimina la propiedad
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # Relación con el viajero que hizo la reserva, elimina la reserva si se elimina el viajero
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    # Campo de fecha de entrada (check-in)
    check_in = models.DateField()
    # Campo de fecha de salida (check-out)
    check_out = models.DateField()
    # Fecha en que se creó la reserva, se asigna automáticamente al crearla
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra el título de la propiedad y el usuario del viajero
    def __str__(self):
        return f"Booking for {self.property.title} by {self.traveler.user.username}"


from django.db import models

# Modelo para almacenar imágenes de las opiniones
class ReviewImage(models.Model):
    # Relación con la opinión a la que pertenece la imagen
    review = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='images')
    # Imagen asociada a la opinión
    image = models.ImageField(upload_to='review_images/')
    # Texto opcional para describir la imagen
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for review {self.review.id}"

# Tabla para las opiniones
class Review(models.Model):
    # Relación con la propiedad a la que pertenece la opinión
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # Relación con el viajero que deja la opinión
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    # Campo de valoración, un número entero
    rating = models.IntegerField()
    # Comentario opcional de la opinión
    comment = models.TextField(blank=True, null=True)
    # Fecha en que se creó la opinión, se asigna automáticamente al crearla
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra la propiedad y el nombre del viajero
    def __str__(self):
        return f"Review for {self.property.title} by {self.traveler.user.username}"

    # Verificación de que la opinión tenga al menos 5 fotos asociadas
    def clean(self):
        if self.images.count() < 5:
            raise ValidationError("A review must have at least 5 images.")



# Tabla para la disponibilidad
class Availability(models.Model):
    # Relación con la propiedad para la que se establece la disponibilidad
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # Fecha específica en la que la propiedad está disponible
    available_date = models.DateField()
    # Estado de disponibilidad (si está disponible o no)
    is_available = models.BooleanField(default=True)
    # Fecha en que se creó la entrada de disponibilidad, se asigna automáticamente
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra la fecha disponible y el título de la propiedad
    def __str__(self):
        return f"Availability on {self.available_date} for {self.property.title}"


# Tabla para los precios
class Pricing(models.Model):
    # Relación con la propiedad a la que pertenece el precio
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # Precio de la propiedad, con hasta 10 dígitos y 2 decimales
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Fecha en la que este precio entra en vigor
    effective_date = models.DateField()
    # Fecha en que se creó la entrada de precio, se asigna automáticamente
    created_at = models.DateTimeField(auto_now_add=True)

    # Representación del objeto como una cadena, muestra el precio y la fecha efectiva
    def __str__(self):
        return f"Price for {self.property.title} effective from {self.effective_date}"