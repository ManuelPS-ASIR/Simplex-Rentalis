from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User, Identidades, Propiedades, Galeria
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
class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedades
        fields = [
            'nombre', 'descripcion', 'direccion', 'precio_noche', 'calificacion', 'permite_mascotas', 'en_mantenimiento', 'capacidad_maxima'
        ]
class IdentidadForm(forms.ModelForm):
    class Meta:
        model = Identidades
        fields = ['tipo_documento', 'numero_documento', 'fecha_expedicion', 'primer_apellido', 
                  'segundo_apellido', 'nombre', 'sexo']
    
    # Definir el widget para el campo 'fecha_expedicion'
    fecha_expedicion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Definir el widget para 'numero_documento' y limitar a 9 caracteres
    numero_documento = forms.CharField(
        max_length=9,  # Limitar a 9 caracteres
        widget=forms.TextInput(attrs={'maxlength': '9'})  # Establecer atributo maxlength en HTML
    )

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get("numero_documento")
        
                # Verificar que el número de documento tenga exactamente 9 caracteres
        if len(numero_documento) != 9:
            raise forms.ValidationError("El número de documento debe tener exactamente 9 caracteres.")
        
        # Expresión regular para validar el formato de un DNI español: 8 dígitos + letra
        if not re.match(r'^\d{8}[A-Za-z]$', numero_documento):
            raise forms.ValidationError("El número de documento debe tener el formato de un DNI español: 8 dígitos seguidos de una letra.")
        
        return numero_documento
from django import forms
from .models import Reservas

class ReservaForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    cantidad_personas = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'value': 1, 'min': 1}),
        required=True
    )

    class Meta:
        model = Reservas
        fields = ['fecha_inicio', 'fecha_fin', 'cantidad_personas', 'mascotas', 'tipo_mascota']
