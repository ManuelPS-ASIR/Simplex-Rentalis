import os
import shutil
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
        media_folder = 'media/propiedades'

        # Crear la carpeta de destino si no existe
        os.makedirs(media_folder, exist_ok=True)

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
                    try:
                        # Buscar el usuario propietario
                        propietario = User.objects.filter(username=row['Propietario']).first()
                        if not propietario:
                            self.stdout.write(self.style.ERROR(f'Propietario {row["Propietario"]} no encontrado. Omitiendo propiedad {row["Nombre"]}.'))
                            continue
                        
                        # Dividir la dirección
                        direccion_completa = row['Direccion'].split(',')
                        if len(direccion_completa) != 6:
                            self.stdout.write(self.style.ERROR(f'Dirección mal formada para la propiedad {row["Nombre"]}. Omitiendo. Dirección: {row["Direccion"]}'))
                            continue
                        
                        calle, numero_casa, codigo_postal, ciudad, co_autonoma, provincia = [part.strip() for part in direccion_completa]

                        # Crear la dirección
                        try:
                            direccion_instance = Direcciones.objects.create(
                                calle=calle,
                                numero_casa=numero_casa,
                                codigo_postal=codigo_postal,
                                ciudad=ciudad,
                                co_autonoma=co_autonoma,
                                provincia=provincia,
                                pais="España"  # Asumiendo que el país siempre es España para este contexto
                            )
                        except ValidationError as e:
                            self.stdout.write(self.style.ERROR(f'Error al crear la dirección para la propiedad {row["Nombre"]}: {e.messages}. Dirección: {row["Direccion"]}. Omitiendo.'))
                            continue

                        # Verificar si ya existe una propiedad con la misma dirección y propietario
                        if Propiedades.objects.filter(direccion=direccion_instance, propietario=propietario).exists():
                            self.stdout.write(self.style.ERROR(f'Propiedad con dirección {direccion_instance} y propietario {propietario} ya existe. Omitiendo {row["Nombre"]}.'))
                            continue

                        # Crear la propiedad
                        try:
                            propiedad = Propiedades.objects.create(
                                nombre=row['Nombre'],
                                descripcion=row['Descripcion'],
                                direccion=f"{direccion_instance.calle}, {direccion_instance.numero_casa}, {direccion_instance.ciudad}",
                                precio_noche=float(row['Precio']),
                                propietario=propietario,
                                calificacion=float(row['Calificacion']),
                                permite_mascotas=row['Pets'].strip().lower() == 'true',
                                en_mantenimiento=row['Mantenimiento'].strip().lower() == 'true',
                                capacidad_maxima=int(row['Huespedes']),
                                cantidad_banos=int(row['Banos']),
                                cantidad_dormitorios=int(row['Dormitorios']),
                            )
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error al crear la propiedad {row["Nombre"]}: {e}. Datos: {row}. Omitiendo.'))
                            continue

                        # Asociar imágenes a la propiedad y marcar la primera como portada
                        galeria_prefix = row['Imagenes']
                        primera_imagen = True
                        for filename in os.listdir(images_folder):
                            if filename.startswith(galeria_prefix):
                                src_image_path = os.path.join(images_folder, filename)
                                dest_image_path = os.path.join(media_folder, filename)
                                shutil.copy(src_image_path, dest_image_path)
                                Galeria.objects.create(
                                    propiedad=propiedad,
                                    imagen=dest_image_path,
                                    portada=primera_imagen
                                )
                                primera_imagen = False

                        self.stdout.write(self.style.SUCCESS(f'Propiedad {propiedad.nombre} creada con éxito.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error procesando la propiedad {row["Nombre"]}: {e}. Datos: {row}. Omitiendo.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"El archivo {csv_file} no se encontró. Verifica la ruta."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {str(e)}"))
