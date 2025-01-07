import os
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from SimplexRentalisAPP.models import User, IdentidadUsuario

class Command(BaseCommand):
    help = 'Poblar la tabla de identidades de usuarios desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de identidades de personas')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Leer el archivo CSV
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                identidad = IdentidadUsuario.objects.create(
                    tipo_documento=row['Tipo documento'],
                    numero_documento=row['Número documento'],
                    fecha_expedicion=row['Fecha expedición'],
                    primer_apellido=row['Primer apellido'],
                    segundo_apellido=row.get('Segundo apellido', ''),
                    nombre=row['Nombre'],
                    sexo=row.get('Sexo', 'otro'),
                )
                
                # Asignar la ruta de la imagen de avatar
                avatar_path = row['Imagen de perfil']
                if not os.path.exists(os.path.join('static/comand_admin/fotos1', avatar_path.split('/')[-1])):
                    avatar_path = 'media/defaults/default_avatar.png'
                else:
                    avatar_path = os.path.join('static/comand_admin/fotos1', avatar_path.split('/')[-1])
                
                # Crear un usuario asociado a la identidad
                user = User.objects.create(
                    username=row['Nombre de usuario'],
                    email=row['Correo electrónico'],
                    telefono=row['Teléfono móvil'],
                    password=make_password(row['Contraseña']),
                    genero=row['Género'],
                    fecha_nacimiento=row['Fecha de nacimiento'],
                    avatar=avatar_path,
                    identidad_usuario=identidad,
                    es_propietario=row.get('es_propietario', 'False') == 'True'
                )

                self.stdout.write(self.style.SUCCESS(f'Usuario {user.username} creado.'))
