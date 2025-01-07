import os
import csv
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Propiedades, Galeria

class Command(BaseCommand):
    help = 'Eliminar las propiedades especificadas en un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de propiedades')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        media_folder = 'media/propiedades'

        # Leer el archivo CSV con delimitador explícito
        try:
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                
                # Validar que el CSV tiene las columnas esperadas
                expected_columns = [
                    'Nombre', 'Descripcion', 'Direccion', 'Precio', 'Propietario',
                    'Calificacion', 'Pets', 'Mantenimiento', 'Huespedes', 'Banos', 'Dormitorios', 'Imagenes'
                ]
                if reader.fieldnames != expected_columns:
                    self.stdout.write(self.style.ERROR(
                        f"Las columnas del CSV no coinciden con las esperadas: {expected_columns}. Actual: {reader.fieldnames}."
                    ))
                    return

                for row in reader:
                    propiedad_nombre = row['Nombre']
                    propiedades = Propiedades.objects.filter(nombre=propiedad_nombre)
                    if propiedades.exists():
                        for propiedad in propiedades:
                            # Borrar las imágenes asociadas
                            galerias = Galeria.objects.filter(propiedad=propiedad)
                            for galeria in galerias:
                                if galeria.imagen and os.path.exists(galeria.imagen.path):
                                    os.remove(galeria.imagen.path)
                                galeria.delete()
                            propiedad.delete()
                        self.stdout.write(self.style.SUCCESS(f'Propiedades con nombre {propiedad_nombre} eliminadas con éxito, junto con sus imágenes asociadas.'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Propiedad {propiedad_nombre} no encontrada.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"El archivo {csv_file} no se encontró. Verifica la ruta."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {str(e)}"))
