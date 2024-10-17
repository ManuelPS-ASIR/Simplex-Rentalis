from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    correo = models.EmailField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_propietario = models.BooleanField(default=False)

    def __str__(self):
        return self.correo


class Propiedad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    calificacion = models.FloatField(default=0.0)
    porcentaje_reserva = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.titulo


class Imagen(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes/')  # Change from URLField to ImageField
    es_portada = models.BooleanField(default=False)

    def __str__(self):
        return f'Imagen de {self.propiedad}'

    def clean(self):
        # Optional: Validate image size or type if needed
        pass


class Opinion(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    imagen = models.ImageField(upload_to='opiniones/', blank=True, null=True)  # New ImageField

    class Meta:
        unique_together = ('propiedad', 'usuario')

    def __str__(self):
        return f'Opinion of {self.usuario} on {self.propiedad}'

    def clean(self):
        # Optional: Validate image size or type if needed
        pass

class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    adultos = models.IntegerField(default=0)
    ninos = models.IntegerField(default=0)
    mascotas = models.BooleanField(default=False)
    tipo_mascota = models.CharField(max_length=10, choices=[
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('otro', 'Otro'),
    ], blank=True, null=True)
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reserva de {self.usuario} para {self.propiedad}'


class DocumentoIdentidad(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=30, choices=[
        ('DNI', 'DNI'),
        ('carnet de conducir', 'Carnet de Conducir'),
        ('pasaporte', 'Pasaporte'),
    ])
    numero_documento = models.CharField(max_length=50, unique=True)
    fecha_expedicion = models.DateField()
    primer_apellido = models.CharField(max_length=255)
    segundo_apellido = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    sexo = models.CharField(max_length=10, choices=[
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
    ])
    fecha_nacimiento = models.DateField()
    pais_nacionalidad = models.CharField(max_length=100)
    fecha_entrada = models.DateField()

    def clean(self):
        if self.fecha_expedicion < self.fecha_nacimiento:
            raise ValidationError('La fecha de expedición no puede ser anterior a la fecha de nacimiento.')

    def __str__(self):
        return f'Documento de identidad de {self.nombre} {self.primer_apellido}'