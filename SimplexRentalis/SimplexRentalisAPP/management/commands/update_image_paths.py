from django.core.management.base import BaseCommand
from SimplexRentalisAPP.models import Galeria, User

class Command(BaseCommand):
    help = "Convierte las rutas de imágenes en la base de datos de .png a .webp"

    def handle(self, *args, **kwargs):
        # Actualizar imágenes en Galeria
        galeria_actualizadas = 0
        for obj in Galeria.objects.all():
            if obj.imagen.name.endswith('.png'):
                nueva_ruta = obj.imagen.name.replace('.png', '.webp')
                obj.imagen.name = nueva_ruta
                obj.save()
                galeria_actualizadas += 1

        # Actualizar avatares en User
        avatares_actualizados = 0
        for user in User.objects.all():
            if user.avatar.name.endswith('.png'):
                nueva_ruta = user.avatar.name.replace('.png', '.webp')
                user.avatar.name = nueva_ruta
                user.save()
                avatares_actualizados += 1

        # Mensaje de confirmación
        self.stdout.write(
            self.style.SUCCESS(
                f"Actualización completada: {galeria_actualizadas} imágenes en Galeria y {avatares_actualizados} avatares en User."
            )
        )
