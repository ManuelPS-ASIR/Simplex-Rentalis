import os
import csv
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Propiedades, User, Galeria, Direcciones
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Poblar la tabla de propiedades desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de propiedades')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        images_folder = 'static/comand_admin/fotos2'

        # Leer el archivo CSV
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Buscar el usuario propietario
                propietario = User.objects.filter(username=row['Propietario']).first()
                if not propietario:
                    self.stdout.write(self.style.ERROR(f'Propietario {row["Propietario"]} no encontrado. Omitiendo.'))
                    continue
                
                # Dividir la dirección en sus componentes
                direccion_completa = row['Dirección completa (calle, número, CP, ciudad, comunidad autónoma, provincia, país)'].split(', ')
                if len(direccion_completa) != 7:
                    self.stdout.write(self.style.ERROR(f'Dirección mal formada para la propiedad {row["Nombre de la propiedad"]}. Omitiendo.'))
                    continue
                
                calle, numero_casa, codigo_postal, ciudad, co_autonoma, provincia, pais = direccion_completa

                # Crear la dirección
                try:
                    direccion_instance = Direcciones.objects.create(
                        calle=calle,
                        numero_casa=numero_casa,
                        codigo_postal=codigo_postal,
                        ciudad=ciudad,
                        co_autonoma=co_autonoma,
                        provincia=provincia,
                        pais=pais
                    )
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Error al crear la dirección para la propiedad {row["Nombre de la propiedad"]}: {e.messages}. Omitiendo.'))
                    continue

                # Crear la propiedad
                propiedad = Propiedades.objects.create(
                    nombre=row['Nombre de la propiedad'],
                    descripcion=row['Descripción detallada'],
                    direccion=f"{direccion_instance.calle}, {direccion_instance.numero_casa}, {direccion_instance.ciudad}",
                    precio_noche=row['Precio por noche en EUR'],
                    propietario=propietario,
                    calificacion=row['Calificación (1-5)'],
                    permite_mascotas=row['¿Permite mascotas? (True/False)'] == 'True',
                    en_mantenimiento=row['¿En mantenimiento? (True/False)'] == 'True',
                    capacidad_maxima=row['Capacidad máxima de huéspedes'],
                    cantidad_banos=row['Cantidad de baños'],
                    cantidad_dormitorios=row['Cantidad de dormitorios'],
                )

                # Asociar imágenes a la propiedad y marcar la primera como portada
                galeria_prefix = row['Prefijo de la galería de imágenes']
                primera_imagen = True
                for filename in os.listdir(images_folder):
                    if filename.startswith(galeria_prefix):
                        image_path = os.path.join(images_folder, filename)
                        Galeria.objects.create(
                            propiedad=propiedad,
                            imagen=image_path,
                            portada=primera_imagen
                        )
                        primera_imagen = False

                self.stdout.write(self.style.SUCCESS(f'Propiedad {propiedad.nombre} creada con éxito.'))
