import os
import csv
from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import User, IdentidadUsuario

class Command(BaseCommand):
    help = 'Borrar las identidades de usuarios de prueba desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de identidades de personas')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Leer el archivo CSV
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                numero_documento = row['Número documento']

                # Buscar la identidad con el número de documento
                identidad = IdentidadUsuario.objects.filter(numero_documento=numero_documento).first()
                
                if identidad:
                    try:
                        usuario = identidad.usuario_asociado
                        username = usuario.username
                        avatar_path = usuario.avatar.path if usuario.avatar else None
                        numero_documento = identidad.numero_documento

                        # Eliminar el usuario asociado
                        usuario.delete()
                        self.stdout.write(self.style.SUCCESS(f'Usuario {username} con documento {numero_documento} borrado.'))

                        # Eliminar la imagen de perfil si no es la imagen por defecto
                        if avatar_path and 'defaults/default_avatar.png' not in avatar_path:
                            if os.path.exists(avatar_path):
                                os.remove(avatar_path)
                                self.stdout.write(self.style.SUCCESS(f'Imagen de perfil {avatar_path} borrada.'))
                    except User.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'No se encontró usuario asociado a la identidad con documento {numero_documento}.'))

                    # Eliminar la identidad
                    identidad.delete()
                    self.stdout.write(self.style.SUCCESS(f'Identidad con documento {numero_documento} borrada.'))
                else:
                    self.stdout.write(self.style.ERROR(f'No se encontró identidad con documento {numero_documento}.'))
