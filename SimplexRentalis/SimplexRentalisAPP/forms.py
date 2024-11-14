from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

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
        }
    )
    telefono = forms.CharField(
        label=_("Teléfono"),
        max_length=9,
        required=True,
        error_messages={
            'invalid': _("Ingrese un número de móvil español válido.")
        }
    )
    fecha_nacimiento = forms.DateField(
        label=_("Fecha de nacimiento"),
        required=False,
        error_messages={
            'invalid': _("Ingrese una fecha válida.")
        }
    )
    genero = forms.ChoiceField(
        label=_("Género"),
        choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')],
        required=False,
        error_messages={
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
