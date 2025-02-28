from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User, IdentidadReserva, IdentidadUsuario, Propiedades, Galeria
import re
from datetime import date
import dns.resolver
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date
import re
import dns.resolver
from .models import User

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
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        error_messages = {
            'password2': {
                'password_mismatch': _("Las contraseñas no coinciden."),
            },
        }

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

class IdentidadUsuarioForm(forms.ModelForm):
    class Meta:
        model = IdentidadUsuario
        fields = ['tipo_documento', 'numero_documento', 'fecha_expedicion', 'primer_apellido', 'segundo_apellido', 'nombre', 'sexo']
    
    fecha_expedicion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    numero_documento = forms.CharField(
        max_length=9,
        widget=forms.TextInput(attrs={'maxlength': '9'})
    )

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get("numero_documento")
        if len(numero_documento) != 9:
            raise forms.ValidationError("El número de documento debe tener exactamente 9 caracteres.")
        if not re.match(r'^\d{8}[A-Za-z]$', numero_documento):
            raise forms.ValidationError("El número de documento debe tener el formato de un DNI español: 8 dígitos seguidos de una letra.")
        return numero_documento

class IdentidadPersonaForm(forms.ModelForm):
    class Meta:
        model = IdentidadReserva  # Cambia a IdentidadReserva para las reservas
        fields = ['tipo_documento', 'numero_documento', 'fecha_expedicion', 'primer_apellido', 'segundo_apellido', 'nombre', 'sexo']
    
    fecha_expedicion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    numero_documento = forms.CharField(
        max_length=9,
        widget=forms.TextInput(attrs={'maxlength': '9'})
    )

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get("numero_documento")
        if len(numero_documento) != 9:
            raise forms.ValidationError("El número de documento debe tener exactamente 9 caracteres.")
        if not re.match(r'^\d{8}[A-Za-z]$', numero_documento):
            raise forms.ValidationError("El número de documento debe tener el formato de un DNI español: 8 dígitos seguidos de una letra.")
        return numero_documento
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



from django import forms

class FiltroPropiedadesForm(forms.Form):
    direccion = forms.CharField(required=False, label="Dirección o Lugar", widget=forms.TextInput(attrs={'class': 'form-control'}))
    precio_min = forms.DecimalField(required=False, label="Precio Mínimo", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    precio_max = forms.DecimalField(required=False, label="Precio Máximo", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    calificacion = forms.ChoiceField(required=False, label="Calificación Mínima", choices=[('', 'Cualquiera'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], widget=forms.Select(attrs={'class': 'form-control'}))
    permite_mascotas = forms.ChoiceField(required=False, label="Permite Mascotas", choices=[('', 'Cualquiera'), ('True', 'Sí'), ('False', 'No')], widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Eliminar este campo
    # capacidad_max = forms.IntegerField(required=False, label="Capacidad Máxima", widget=forms.NumberInput(attrs={'class': 'form-control'}))
