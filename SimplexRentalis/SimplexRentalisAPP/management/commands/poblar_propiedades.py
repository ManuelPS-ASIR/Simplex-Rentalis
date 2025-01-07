import os
import csv
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Propiedades, User, Galeria

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

                # Crear la propiedad
                propiedad = Propiedades.objects.create(
                    nombre=row['Nombre'],
                    descripcion=row['Descripcion'],
                    direccion=row['Direccion'],
                    precio_noche=row['Precio por noche'],
                    propietario=propietario,
                    calificacion=row['Calificacion'],
                    permite_mascotas=row['Permite mascotas'] == 'True',
                    en_mantenimiento=row['En mantenimiento'] == 'True',
                    capacidad_maxima=row['Capacidad maxima'],
                    cantidad_banos=row['Cantidad banos'],
                    cantidad_dormitorios=row['Cantidad dormitorios'],
                )

                # Asociar imágenes a la propiedad
                galeria_prefix = row['Galeria']
                for filename in os.listdir(images_folder):
                    if filename.startswith(galeria_prefix):
                        image_path = os.path.join(images_folder, filename)
                        Galeria.objects.create(
                            propiedad=propiedad,
                            imagen=image_path,
                        )

                self.stdout.write(self.style.SUCCESS(f'Propiedad {propiedad.nombre} creada con éxito.'))
