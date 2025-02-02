import os
import glob
import csv
import re
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Propiedades, Direcciones, Galeria, User

class Command(BaseCommand):
    help = 'Poblar la tabla de propiedades desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de propiedades')

    def parse_direccion(self, direccion_str):
        """
        Se espera un string de la forma:
          "Calle y número, Código Postal, Ciudad, Comunidad Autónoma, Provincia, País"
        Se separa la primera parte en calle y número (si se encuentra un número).
        """
        partes = [p.strip() for p in direccion_str.split(',')]
        if len(partes) != 6:
            raise ValueError(f"La dirección debe tener 6 partes separadas por comas. Recibido: {direccion_str}")
        
        # Separar la calle y el número usando una expresión regular.
        match = re.match(r'^(.*?)(\d+)$', partes[0])
        if match:
            calle = match.group(1).strip()
            numero_casa = match.group(2)
        else:
            calle = partes[0]
            numero_casa = ""
        
        # Asignamos el resto de los campos
        codigo_postal = partes[1]
        ciudad = partes[2]
        co_autonoma = partes[3]
        provincia = partes[4]
        pais = partes[5]

        # Se devuelve un diccionario con los datos (numero_puerta se deja vacío)
        return {
            'calle': calle,
            'numero_casa': numero_casa,
            'numero_puerta': None,
            'codigo_postal': codigo_postal,
            'ciudad': ciudad,
            'co_autonoma': co_autonoma,
            'provincia': provincia,
            'pais': pais
        }

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        # Directorio en el que se encuentran las imágenes para las propiedades.
        # Por ejemplo, si usas static/comand_admin/fotos2
        fotos_dir = os.path.join(settings.STATICFILES_DIRS[0], 'comand_admin', 'fotos2')

        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    self.stdout.write(f"Procesando propiedad: {row['Nombre']}")

                    # Parseo de dirección
                    direccion_data = self.parse_direccion(row['Direccion'])
                    direccion_obj = Direcciones.objects.create(
                        calle=direccion_data['calle'],
                        numero_casa=direccion_data['numero_casa'],
                        numero_puerta=direccion_data['numero_puerta'],
                        codigo_postal=direccion_data['codigo_postal'],
                        ciudad=direccion_data['ciudad'],
                        co_autonoma=direccion_data['co_autonoma'],
                        provincia=direccion_data['provincia'],
                        pais=direccion_data['pais']
                    )

                    # Buscar el propietario (User) según el username
                    propietario_username = row['Propietario']
                    try:
                        propietario = User.objects.get(username=propietario_username)
                    except User.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Propietario {propietario_username} no encontrado. Omitiendo propiedad {row['Nombre']}."))
                        continue

                    # Crear la propiedad
                    propiedad_obj = Propiedades.objects.create(
                        nombre=row['Nombre'],
                        descripcion=row['Descripcion'],
                        direccion=direccion_obj,
                        precio_noche=Decimal(row['Precio']),
                        propietario=propietario,
                        calificacion=Decimal(row['Calificacion']),
                        permite_mascotas=(row['Pets'].strip().lower() == 'true'),
                        en_mantenimiento=(row['Mantenimiento'].strip().lower() == 'true'),
                        capacidad_maxima=int(row['Huespedes']),
                        cantidad_banos=int(row['Banos']),
                        cantidad_dormitorios=int(row['Dormitorios'])
                    )

                    # Procesar imágenes: el CSV contiene un patrón (por ejemplo, "saragonzalez85_imagen_*")
                    imagen_pattern = row['Imagenes']
                    pattern = os.path.join(fotos_dir, imagen_pattern)
                    matched_files = glob.glob(pattern)
                    if not matched_files:
                        self.stdout.write(self.style.WARNING(f"No se encontraron imágenes para la propiedad {row['Nombre']}."))
                    else:
                        # Crear entradas en la galería. Se marca la primera como portada.
                        for idx, file_path in enumerate(sorted(matched_files)):
                            # Obtener la ruta relativa al directorio de medios
                            # Se asume que en MEDIA_ROOT se almacenarán las imágenes copiadas o linkeadas.
                            # Ajusta este comportamiento según tu configuración.
                            rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                            Galeria.objects.create(
                                propiedad=propiedad_obj,
                                imagen=rel_path,
                                descripcion=f"Imagen {idx+1} de {row['Nombre']}",
                                portada=(idx == 0)
                            )
                        self.stdout.write(self.style.SUCCESS(f"Se crearon {len(matched_files)} imágenes para {row['Nombre']}."))
                    
                    self.stdout.write(self.style.SUCCESS(f"Propiedad '{propiedad_obj.nombre}' creada correctamente."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error procesando fila {row}: {str(e)}"))
