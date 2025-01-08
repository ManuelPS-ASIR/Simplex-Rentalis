import os
import glob
import csv
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from SimplexRentalisAPP.models import User, IdentidadUsuario

class Command(BaseCommand):
    help = 'Poblar la tabla de identidades de usuarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de identidades de personas')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Directorio base para los avatares personalizados
        avatar_dir = os.path.join(settings.STATICFILES_DIRS[0], 'comand_admin', 'fotos1')
        default_avatar_path = 'defaults/default_avatar.png'

        # Leer el archivo CSV
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Convertir las fechas al formato correcto
                    fecha_expedicion = datetime.strptime(row['Fecha expedición'], '%d/%m/%Y').strftime('%Y-%m-%d')
                    fecha_nacimiento = datetime.strptime(row['Fecha de nacimiento'], '%d/%m/%Y').strftime('%Y-%m-%d')

                    # Verificar si ya existe una identidad con el mismo número de documento
                    if IdentidadUsuario.objects.filter(numero_documento=row['Número documento']).exists():
                        self.stdout.write(self.style.ERROR(f"Identidad con número de documento {row['Número documento']} ya existe. Omitiendo."))
                        continue

                    # Crear identidad
                    identidad = IdentidadUsuario.objects.create(
                        tipo_documento=row['Tipo documento'],
                        numero_documento=row['Número documento'],
                        fecha_expedicion=fecha_expedicion,
                        primer_apellido=row['Primer apellido'],
                        segundo_apellido=row.get('Segundo apellido', ''),
                        nombre=row['Nombre'],
                        sexo=row.get('Sexo', 'otro'),
                    )

                    # Procesar la ruta del avatar con soporte para `.*`
                    avatar_filename = os.path.basename(row['Imagen de perfil'])
                    avatar_base, avatar_ext = os.path.splitext(avatar_filename)
                    
                    # Buscar archivo con nombre base independientemente de la extensión
                    matched_files = glob.glob(os.path.join(avatar_dir, f"{avatar_base}.*"))
                    if matched_files:
                        # Ruta relativa al directorio de medios
                        avatar_path = os.path.relpath(matched_files[0], settings.MEDIA_ROOT)
                        self.stdout.write(self.style.SUCCESS(f"Archivo encontrado para {row['Nombre de usuario']}: {os.path.basename(matched_files[0])}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Avatar no encontrado para {row['Nombre de usuario']}. Usando avatar predeterminado."))
                        avatar_path = default_avatar_path

                    # Verificar si ya existe un usuario con el mismo teléfono
                    if User.objects.filter(telefono=row['Teléfono móvil']).exists():
                        self.stdout.write(self.style.ERROR(f"Usuario con teléfono {row['Teléfono móvil']} ya existe. Omitiendo."))
                        continue

                    # Crear usuario
                    user = User.objects.create(
                        username=row['Nombre de usuario'],
                        email=row['Correo electrónico'],
                        telefono=row['Teléfono móvil'],
                        password=make_password(row['Contraseña']),
                        genero=row['Género'],
                        fecha_nacimiento=fecha_nacimiento,
                        avatar=avatar_path,  # Ruta relativa
                        identidad_usuario=identidad,
                        es_propietario=row.get('es_propietario', 'False') == 'True'
                    )

                    self.stdout.write(self.style.SUCCESS(f'Usuario {user.username} creado.'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error procesando fila {row}: {str(e)}"))
