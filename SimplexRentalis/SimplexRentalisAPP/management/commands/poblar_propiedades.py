import os
import glob
import csv
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Propiedades, User, Galeria, Direcciones
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Poblar la tabla de propiedades desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de propiedades')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        images_folder = os.path.join(settings.STATICFILES_DIRS[0], 'comand_admin', 'fotos2')  # Ruta absoluta
        media_folder = os.path.join(settings.MEDIA_ROOT, 'propiedades')  # Carpeta donde se almacenarán las imágenes

        # Leer el archivo CSV con delimitador explícito
        try:
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')

                # Validar que el CSV tiene las columnas esperadas
                expected_columns = {
                    'Nombre', 'Descripcion', 'Direccion', 'Precio', 'Propietario',
                    'Calificacion', 'Pets', 'Mantenimiento', 'Huespedes', 'Banos', 'Dormitorios', 'Imagenes'
                }
                if set(reader.fieldnames) != expected_columns:
                    self.stdout.write(self.style.ERROR(
                        f"Las columnas del CSV no coinciden con las esperadas. "
                        f"Esperado: {expected_columns}, Actual: {reader.fieldnames}."
                    ))
                    return

                for row in reader:
                    try:
                        # Buscar el usuario propietario
                        propietario = User.objects.filter(username=row['Propietario']).first()
                        if not propietario:
                            self.stdout.write(self.style.ERROR(
                                f'Propietario {row["Propietario"]} no encontrado. Omitiendo propiedad {row["Nombre"]}.'
                            ))
                            continue
                        
                        # Dividir la dirección
                        direccion_completa = row['Direccion'].split(',')
                        if len(direccion_completa) != 6:
                            self.stdout.write(self.style.ERROR(
                                f'Dirección mal formada para la propiedad {row["Nombre"]}. Omitiendo. Dirección: {row["Direccion"]}'
                            ))
                            continue
                        
                        calle, numero_casa, codigo_postal, ciudad, co_autonoma, provincia = [
                            part.strip() for part in direccion_completa
                        ]

                        # Crear la dirección
                        try:
                            direccion_instance, created = Direcciones.objects.get_or_create(
                                calle=calle,
                                numero_casa=numero_casa,
                                codigo_postal=codigo_postal,
                                ciudad=ciudad,
                                co_autonoma=co_autonoma,
                                provincia=provincia,
                                pais="España"
                            )
                        except ValidationError as e:
                            self.stdout.write(self.style.ERROR(
                                f'Error al crear la dirección para la propiedad {row["Nombre"]}: {e.messages}. '
                                f'Dirección: {row["Direccion"]}. Omitiendo.'
                            ))
                            continue

                        # Verificar si ya existe una propiedad con la misma dirección y propietario
                        if Propiedades.objects.filter(direccion=direccion_instance, propietario=propietario).exists():
                            self.stdout.write(self.style.ERROR(
                                f'Propiedad con dirección {direccion_instance} y propietario {propietario} ya existe. '
                                f'Omitiendo {row["Nombre"]}.'
                            ))
                            continue

                        # Validar imágenes
                        galeria_prefix = row['Imagenes']
                        imagenes_encontradas = glob.glob(os.path.join(images_folder, f"{galeria_prefix}*.png"))

                        if len(imagenes_encontradas) < 5:
                            self.stdout.write(self.style.ERROR(
                                f'No se encontraron al menos 5 imágenes para la propiedad {row["Nombre"]} '
                                f'con prefijo {galeria_prefix}. Omitiendo. Ruta buscada: {images_folder}'
                            ))
                            continue
                        else:
                            self.stdout.write(self.style.SUCCESS(
                                f"Se encontraron {len(imagenes_encontradas)} imágenes para la propiedad {row['Nombre']} "
                                f"en las rutas: {', '.join(imagenes_encontradas)}"
                            ))

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
                            self.stdout.write(self.style.ERROR(
                                f'Error al crear la propiedad {row["Nombre"]}: {e}. Datos: {row}. Omitiendo.'
                            ))
                            continue

                        # Copiar imágenes a la carpeta de media/propiedades y asociarlas a la propiedad
                        primera_imagen = True
                        for image_path in imagenes_encontradas:
                            destino = os.path.join(media_folder, os.path.basename(image_path))
                            try:
                                shutil.copy(image_path, destino)
                                Galeria.objects.create(
                                    propiedad=propiedad,
                                    imagen=os.path.relpath(destino, settings.MEDIA_ROOT),
                                    portada=primera_imagen
                                )
                                self.stdout.write(self.style.SUCCESS(
                                    f"Imagen {os.path.relpath(image_path, images_folder)} asociada exitosamente a la propiedad {row['Nombre']} y copiada a {destino}."
                                ))
                                primera_imagen = False
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(
                                    f'Error al asociar imagen {image_path} con la propiedad {row["Nombre"]}: {e}'
                                ))
                                continue

                        self.stdout.write(self.style.SUCCESS(
                            f'Propiedad {propiedad.nombre} creada con éxito con ID {propiedad.id}.'
                        ))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'Error procesando la propiedad {row["Nombre"]}: {e}. Datos: {row}. Omitiendo.'
                        ))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"El archivo {csv_file} no se encontró. Verifica la ruta."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {str(e)}"))
