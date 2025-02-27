import os
from PIL import Image
from django.core.management.base import BaseCommand

# Directorios donde buscar imágenes
DIRECTORIOS = [
    "media",
    "static/comand_admin/fotos1",
    "static/comand_admin/fotos2"
]

# Extensiones válidas para conversión
EXTENSIONES_VALIDAS = ('.jpg', '.jpeg', '.png')

class Command(BaseCommand):
    help = ("Convierte imágenes .jpg, .jpeg y .png a formato WebP y elimina la versión original "
            "si ya existe la WebP. Además, si hay imágenes duplicadas con distintas extensiones, "
            "se conserva la versión WebP y se elimina la otra.")

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando la conversión y eliminación de archivos duplicados en los directorios especificados...\n")
        
        files_to_delete = set()
        converted_count = 0
        duplicate_deleted_count = 0
        errors = []

        for directorio in DIRECTORIOS:
            if not os.path.exists(directorio):
                self.stdout.write(f"Directorio no encontrado: {directorio}\n")
                continue

            for raiz, _, archivos in os.walk(directorio):
                for archivo in archivos:
                    ruta_completa = os.path.join(raiz, archivo)
                    # Procesar solo imágenes con las extensiones válidas (que no sean ya .webp)
                    if archivo.lower().endswith(EXTENSIONES_VALIDAS) and not archivo.lower().endswith('.webp'):
                        base, _ = os.path.splitext(ruta_completa)
                        webp_path = base + ".webp"

                        if os.path.exists(webp_path):
                            # Ya existe la versión WebP; marcar el original para eliminarlo.
                            files_to_delete.add(ruta_completa)
                            self.stdout.write(f"Duplicado detectado: {ruta_completa} tiene su versión WebP ({webp_path}). Marcado para eliminación.\n")
                            duplicate_deleted_count += 1
                        else:
                            # Intentar la conversión
                            if self.convertir_a_webp(ruta_completa, webp_path):
                                files_to_delete.add(ruta_completa)
                                converted_count += 1
                            else:
                                errors.append(f"Fallo al convertir: {ruta_completa}")

        # Eliminar archivos originales convertidos o duplicados
        for f in files_to_delete:
            try:
                os.remove(f)
                self.stdout.write(f"Eliminado: {f}\n")
            except Exception as e:
                error_msg = f"Error al eliminar {f}: {e}"
                errors.append(error_msg)
                self.stderr.write(error_msg + "\n")

        # Resumen final
        self.stdout.write("\nResumen de la operación:")
        self.stdout.write(f"  Archivos convertidos a WebP y eliminados: {converted_count}")
        self.stdout.write(f"  Archivos duplicados eliminados: {duplicate_deleted_count}")
        if errors:
            self.stderr.write("Se presentaron los siguientes errores:")
            for err in errors:
                self.stderr.write(err)
        else:
            self.stdout.write("Operación completada sin errores.")

    def convertir_a_webp(self, ruta_imagen, webp_path):
        """Convierte una imagen a formato WebP y la guarda en webp_path.
           Retorna True si la conversión fue exitosa, False en caso contrario.
        """
        try:
            with Image.open(ruta_imagen) as imagen:
                imagen.save(webp_path, "WEBP", quality=80)
            self.stdout.write(f"Convertido: {ruta_imagen} → {webp_path}\n")
            return True
        except Exception as e:
            self.stderr.write(f"Error al convertir {ruta_imagen}: {e}\n")
            return False
