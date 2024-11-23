from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re
from datetime import date
import dns.resolver


class RegistroForm(UserCreationForm):
    username = forms.CharField(
        label=_("Nombre de usuario"),
        max_length=30,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'unique': _("Este nombre de usuario ya está en uso."),
        }
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        max_length=254,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'unique': _("Este correo electrónico ya está en uso."),
            'invalid': _("Ingrese un correo electrónico válido."),
        }
    )
    telefono = forms.CharField(
        label=_("Teléfono"),
        max_length=9,
        required=True,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid': _("Ingrese un número de móvil español válido."),
            'unique': _("Este número de móvil español ya está en uso."),
        }
    )
    fecha_nacimiento = forms.DateField(
        label=_("Fecha de nacimiento"),
        required=True,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid': _("Ingrese una fecha válida.")
        }
    )
    genero = forms.ChoiceField(
        label=_("Género"),
        choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')],
        required=False,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid_choice': _("Seleccione una opción válida.")
        }
    )
    avatar = forms.ImageField(
        label=_("Avatar"),
        required=False,
        error_messages={
            'invalid': _("Ingrese una imagen válida.")
        }
    )

    class Meta:
        model = User
        fields = ("username", "email", "telefono", "fecha_nacimiento", "genero", "avatar", "password1", "password2")
        error_messages = {
            'password2': {
                'password_mismatch': _("Las contraseñas no coinciden."),
            },
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        # Verificar que el número contiene solo números y comienza con 6 o 7
        if not re.match(r'^[67]\d{8}$', telefono):
            raise ValidationError(_("Ingrese un número de móvil español válido. Debe contener 9 dígitos y empezar con 6 o 7."))

        return telefono

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        
        # Verificar la longitud mínima de la contraseña
        if len(password1) < 10:
            raise ValidationError(_("La contraseña debe tener al menos 10 caracteres."))

        # Verificar que contenga al menos una mayúscula
        if not re.search(r'[A-Z]', password1):
            raise ValidationError(_("La contraseña debe contener al menos una letra mayúscula."))

        # Verificar que contenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError(_("La contraseña debe contener al menos un carácter especial."))

        # Verificar que contenga al menos dos números
        if len(re.findall(r'[0-9]', password1)) < 2:
            raise ValidationError(_("La contraseña debe contener al menos dos números."))

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('password1', _("Las contraseñas no coinciden."))
            raise ValidationError(_("Las contraseñas no coinciden."))
        return password2

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
        today = date.today()
        age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

        if age < 18:
            raise ValidationError(_("Debe tener al menos 18 años para registrarse."))

        return fecha_nacimiento

    def clean_email(self):
        email = self.cleaned_data.get("email")
        domain = email.split('@')[1]

        try:
            dns.resolver.resolve(domain, 'MX')
        except dns.resolver.NXDOMAIN:
            raise ValidationError(_("El dominio del correo electrónico no parece ser válido."))
        except dns.resolver.NoAnswer:
            raise ValidationError(_("El dominio del correo electrónico no parece ser válido."))
        except dns.resolver.NoNameservers:
            raise ValidationError(_("El dominio del correo electrónico no parece ser válido."))
        return email


class ConfiguracionCuentaForm(forms.ModelForm):
    username = forms.CharField(
        label=_("Nombre de usuario"),
        max_length=30,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'unique': _("Este nombre de usuario ya está en uso."),
        }
    )
    telefono = forms.CharField(
        label=_("Teléfono"),
        max_length=9,
        required=True,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid': _("Ingrese un número de móvil español válido."),
            'unique': _("Este número de móvil español ya está en uso."),
        }
    )
    fecha_nacimiento = forms.DateField(
        label=_("Fecha de nacimiento"),
        required=True,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid': _("Ingrese una fecha válida.")
        }
    )
    genero = forms.ChoiceField(
        label=_("Género"),
        choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')],
        required=False,
        error_messages={
            'required': _("Este campo es obligatorio."),
            'invalid_choice': _("Seleccione una opción válida.")
        }
    )
    avatar = forms.ImageField(
        label=_("Avatar"),
        required=False,
        error_messages={
            'invalid': _("Ingrese una imagen válida.")
        }
    )

    class Meta:
        model = User
        fields = ("username", "telefono", "fecha_nacimiento", "genero", "avatar")

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if not re.match(r'^[67]\d{8}$', telefono):
            raise ValidationError(_("Ingrese un número de móvil español válido. Debe contener 9 dígitos y empezar con 6 o 7."))
        return telefono

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get("fecha_nacimiento")
        today = date.today()
        age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if age < 18:
            raise ValidationError(_("Debe tener al menos 18 años para registrarse."))
        return fecha_nacimiento

from .models import Propiedades
from .models import Galeria

class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedades
        fields = [
            'nombre', 'descripcion', 'direccion', 'precio_noche', 'calificacion', 'permite_mascotas', 'en_mantenimiento', 'capacidad_maxima'
        ]
# # Formulario para crear una propiedad
# class PropiedadForm(forms.ModelForm):
#     # Este formulario solo tiene los campos de la propiedad (nombre, descripcion, etc.)
#     class Meta:
#         model = Propiedades
#         fields = ['nombre', 'descripcion']  # Solo los campos que estén en Propiedades, no 'imagen'

#     # Campo adicional para cargar las imágenes (no está en el modelo Propiedades)
#     imagenes = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    
#     def save(self, commit=True):
#         # Guardamos la propiedad (sin las imágenes)
#         propiedad = super().save(commit=False)
#         if commit:
#             propiedad.save()

#         # Guardamos las imágenes asociadas a la propiedad en el modelo Galeria
#         imagenes = self.cleaned_data.get('imagenes')
#         if imagenes:
#             for imagen in imagenes:
#                 Galeria.objects.create(propiedad=propiedad, image=imagen)
        
#         return propiedad

# # Formulario para registrar un nuevo usuario
# class RegistroForm(UserCreationForm):
#     avatar = forms.ImageField(required=False)  # Si quieres permitir que el usuario suba un avatar

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'avatar']

# # Formulario para configurar la cuenta del usuario
# class ConfiguracionCuentaForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'avatar']  # Campos que pueden ser modificados

# # Si necesitas un formulario para las imágenes de las propiedades, también puedes incluir uno aquí
# class ImagenPropiedadForm(forms.ModelForm):
#     class Meta:
#         model = Galeria
#         fields = ['image', 'portada']