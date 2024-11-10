from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import re

####################################
##### 0. Modelo de Usuarios #####
####################################
class User(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(
        max_length=10,
        choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')],
        blank=True,
        null=True
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    biografia = models.TextField(blank=True, null=True)
    es_propietario = models.BooleanField(default=False)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def is_viajero(self):
        return not self.es_propietario

    def is_administrador(self):
        return self.es_propietario

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def clean(self):
        # Validación para el campo teléfono (solo números)
        if self.telefono:
            # Eliminar todos los caracteres que no sean números
            self.telefono = re.sub(r'[^0-9]', '', self.telefono)

            # Validar que el teléfono tiene exactamente 9 dígitos
            if len(self.telefono) != 9:
                raise ValidationError("El teléfono debe contener exactamente 9 dígitos.")
            
            # Validación para la fecha de nacimiento (mayor de edad)
            if self.fecha_nacimiento:
                hoy = timezone.localdate()
                edad = hoy.year - self.fecha_nacimiento.year
                if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                    edad -= 1
                if edad < 18:
                    raise ValidationError("El usuario debe ser mayor de 18 años.")

# Señal para actualizar `ultimo_acceso` cuando el usuario inicie sesión
@receiver(user_logged_in)
def actualizar_ultimo_acceso(sender, request, user, **kwargs):
    user.ultimo_acceso = timezone.localtime()  # Usamos localtime para considerar la zona horaria
    user.save()

####################################
##### 1. Modelo de Propiedades #####
####################################
class Propiedades(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    descripcion = models.TextField(max_length=3000, blank=True, null=True)
    direccion = models.CharField(max_length=300, blank=False, null=False)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    propietario = models.ForeignKey('User', on_delete=models.CASCADE, blank=False, null=False)
    calificacion = models.DecimalField(
    default=3.0, 
    blank=False, 
    null=False, 
    validators=[MinValueValidator(1), MaxValueValidator(5)],
    max_digits=2,  # Total de 2 dígitos: 1 antes del punto decimal y 1 después
    decimal_places=1  # 1 lugar después del punto decimal
    )    
    porcentaje_reserva = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=5.0)
    imagen = models.ImageField(upload_to='img/propiedades/', null=False, blank=False)
    permite_mascotas = models.BooleanField(default=False)
    en_mantenimiento = models.BooleanField(default=False)
    capacidad_maxima = models.IntegerField(default=10)  # Limita la cantidad de personas

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['direccion', 'propietario'], name='unique_direccion_propietario')
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        # Validación de porcentaje de reserva
        if not (5 <= self.porcentaje_reserva <= 35):
            raise ValidationError("El porcentaje de reserva debe estar entre 5% y 35%.")
        
        # Validación de la calificación
        if self.calificacion < 1 or self.calificacion > 5:
            raise ValidationError("La calificación debe estar entre 1 y 5.")

    def esta_disponible(self, fecha_inicio, fecha_fin):
        if fecha_inicio >= fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la de fin.")
        if self.en_mantenimiento:
            return False
        # Usamos `exists()` para optimizar la consulta
        if Reservas.objects.filter(
            propiedad=self, 
            fecha_inicio__lt=fecha_fin, 
            fecha_fin__gt=fecha_inicio
        ).exists():
            return False
        return True

###################################
##### 2. Modelo de Reservas #######
###################################
class ReservaPersona(models.Model):
    reserva = models.ForeignKey('Reservas', on_delete=models.CASCADE)
    identidad = models.ForeignKey('Identidades', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reserva', 'identidad'], name='unique_reserva_identidad'),
        ]

class Reservas(models.Model):
    id = models.AutoField(primary_key=True)
    propiedad = models.ForeignKey('Propiedades', on_delete=models.CASCADE, null=False, blank=False)
    usuario = models.ForeignKey('User', on_delete=models.CASCADE, null=False, blank=False)
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_fin = models.DateField(null=False, blank=False)
    fecha_reserva = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    mascotas = models.BooleanField(default=False, null=False, blank=False)
    tipo_mascota = models.CharField(
        max_length=10, 
        choices=[
            ('perro', 'Perro'),
            ('gato', 'Gato'),
            ('otro', 'Otro'),
        ], 
        blank=True,  
        default=None, 
        null=True
    )
    personas = models.ManyToManyField('Identidades', through='ReservaPersona', related_name="reservas", blank=False)

    class Meta:
        indexes = [
            models.Index(fields=['propiedad', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['propiedad']),
            models.Index(fields=['usuario']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['propiedad', 'fecha_inicio', 'fecha_fin'], name='unique_reserva_fecha'),
        ]

    def __str__(self):
        return f'Reserva {self.id} de {self.propiedad.nombre} del {self.fecha_inicio} al {self.fecha_fin}'

    def clean(self):
        hoy = timezone.localdate()
        if self.fecha_inicio <= hoy:
            raise ValidationError("La fecha de inicio debe ser posterior a la fecha actual.")
        
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la de fin.")
        
        if self.fecha_inicio == self.fecha_fin:
            raise ValidationError("La fecha de inicio y la fecha de fin no pueden ser iguales.")
        
        if Reservas.objects.filter(
            propiedad=self.propiedad,
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        ).exclude(id=self.id).exists():
            raise ValidationError("La propiedad ya tiene una reserva en el rango de fechas seleccionado.")
        
        if self.mascotas and not self.propiedad.permite_mascotas:
            raise ValidationError("No se permiten mascotas en esta propiedad.")
        
        if self.mascotas and not self.tipo_mascota:
            raise ValidationError("Debe especificar el tipo de mascota si se ha marcado la opción de mascotas.")
        
        # Validación de personas: Limitar el número de personas a la capacidad máxima
        max_personas = self.propiedad.capacidad_maxima
        if len(self.personas.all()) > max_personas:
            raise ValidationError(f"La cantidad de personas no puede superar {max_personas}.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Realizar la validación completa antes de guardar
        super().save(*args, **kwargs)

###################################
##### 3. Modelo de Identidades ####
###################################
class Identidades(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_documento = models.CharField(max_length=3, choices=[('DNI', 'DNI'), ('PAS', 'Pasaporte')], blank=False, null=False)
    numero_documento = models.CharField(max_length=20, blank=False, null=False)
    usuario = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tipo_documento}: {self.numero_documento}'

    def clean(self):
        # Validación de número de documento según el tipo
        if self.tipo_documento == 'DNI' and not re.match(r'^\d{8}[A-Za-z]$', self.numero_documento):
            raise ValidationError("El DNI debe tener 8 dígitos seguidos de una letra.")
        elif self.tipo_documento == 'PAS' and not re.match(r'^[A-Za-z0-9]{6,9}$', self.numero_documento):
            raise ValidationError("El número de pasaporte debe tener entre 6 y 9 caracteres alfanuméricos.")

###################################
##### 4. Modelo de Opiniones #######
###################################
class Opiniones(models.Model):
    id = models.AutoField(primary_key=True)
    propiedad = models.ForeignKey('Propiedades', on_delete=models.CASCADE)
    usuario = models.ForeignKey('User', on_delete=models.CASCADE)
    calificacion = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()

    def clean(self):
        # Impide que los propietarios dejen opiniones sobre sus propias propiedades
        if self.propiedad.propietario == self.usuario:
            raise ValidationError("Un propietario no puede dejar una opinión sobre su propia propiedad.")
        
        if len(self.comentario) < 10:
            raise ValidationError("El comentario debe tener al menos 10 caracteres.")

    def __str__(self):
        return f'Opinión de {self.usuario.username} para {self.propiedad.nombre}'
