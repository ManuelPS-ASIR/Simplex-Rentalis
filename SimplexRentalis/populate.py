import random
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Usuario, Propiedad, Imagen, Opinion, Reserva, DocumentoIdentidad

class Command(BaseCommand):
    help = 'Crea datos de prueba en la base de datos'

    def handle(self, *args, **kwargs):
        # Crear usuarios
        usuarios = [
            Usuario(correo='usuario1@example.com', contrasena='contrasena123', es_propietario=True),
            Usuario(correo='usuario2@example.com', contrasena='contrasena123', es_propietario=False),
            Usuario(correo='usuario3@example.com', contrasena='contrasena123', es_propietario=False),
        ]
        Usuario.objects.bulk_create(usuarios)

        # Obtener los usuarios creados
        usuario1 = Usuario.objects.get(correo='usuario1@example.com')
        usuario2 = Usuario.objects.get(correo='usuario2@example.com')

        # Crear propiedades
        propiedades = [
            Propiedad(usuario=usuario1, titulo='Hermosa cabaña en la montaña', 
                      direccion='Calle de la Naturaleza, 123, Montaña', 
                      descripcion='Una cabaña acogedora con vistas espectaculares.', 
                      precio=150.00, calificacion=4.5, 
                      porcentaje_reserva=20.00, visitas=100),
            Propiedad(usuario=usuario2, titulo='Apartamento moderno en la ciudad', 
                      direccion='Avenida del Centro, 456, Ciudad', 
                      descripcion='Un apartamento elegante en el corazón de la ciudad.', 
                      precio=200.00, calificacion=4.8, 
                      porcentaje_reserva=15.00, visitas=150),
        ]
        Propiedad.objects.bulk_create(propiedades)

        # Obtener las propiedades creadas
        propiedad1 = Propiedad.objects.get(titulo='Hermosa cabaña en la montaña')
        propiedad2 = Propiedad.objects.get(titulo='Apartamento moderno en la ciudad')

        # Crear imágenes para las propiedades
        imagenes = [
            Imagen(propiedad=propiedad1, imagen='imagenes/cabana.jpg', es_portada=True),
            Imagen(propiedad=propiedad2, imagen='imagenes/apartamento.jpg', es_portada=True),
        ]
        Imagen.objects.bulk_create(imagenes)

        # Crear opiniones
        opiniones = [
            Opinion(propiedad=propiedad1, usuario=usuario2, puntuacion=5, 
                    comentario='¡Increíble experiencia! Recomendado.', 
                    imagen='opiniones/opinion1.jpg'),
            Opinion(propiedad=propiedad2, usuario=usuario1, puntuacion=4, 
                    comentario='Muy bien ubicado y cómodo.', 
                    imagen='opiniones/opinion2.jpg'),
        ]
        Opinion.objects.bulk_create(opiniones)

        # Crear reservas
        reservas = [
            Reserva(usuario=usuario2, propiedad=propiedad1, 
                    fecha_entrada='2024-10-01', fecha_salida='2024-10-07', 
                    adultos=2, ninos=1, mascotas=False, 
                    precio_noche=150.00),
            Reserva(usuario=usuario1, propiedad=propiedad2, 
                    fecha_entrada='2024-11-01', fecha_salida='2024-11-05', 
                    adultos=2, ninos=0, mascotas=True, 
                    tipo_mascota='perro', 
                    precio_noche=200.00),
        ]
        Reserva.objects.bulk_create(reservas)

        # Crear documentos de identidad
        documentos = [
            DocumentoIdentidad(reserva=reservas[0], tipo_documento='DNI', 
                               numero_documento='12345678A', 
                               fecha_expedicion='2020-01-01', 
                               primer_apellido='Gómez', segundo_apellido='Lopez', 
                               nombre='Juan', sexo='masculino', 
                               fecha_nacimiento='1990-05-20', 
                               pais_nacionalidad='España', fecha_entrada='2024-10-01'),
            DocumentoIdentidad(reserva=reservas[1], tipo_documento='Pasaporte', 
                               numero_documento='X12345678', 
                               fecha_expedicion='2018-06-01', 
                               primer_apellido='Fernández', segundo_apellido='Pérez', 
                               nombre='María', sexo='femenino', 
                               fecha_nacimiento='1992-11-15', 
                               pais_nacionalidad='España', fecha_entrada='2024-11-01'),
        ]
        DocumentoIdentidad.objects.bulk_create(documentos)

        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente.'))