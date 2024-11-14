from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User  # Asegúrate de que tu modelo User esté definido en models.py

class RegistroForm(UserCreationForm):
    telefono = forms.CharField(
        max_length=15, 
        label="telefono", 
        required=True
    )
    genero = forms.ChoiceField(
        choices=[('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')], 
        label="genero", 
        required=True
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1900, 2100)), 
        label="fecha_nacimiento", 
        required=True
    )
    avatar = forms.ImageField(
        required=False, 
        label="avatar"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'telefono', 'genero', 'fecha_nacimiento', 'avatar', 'password1', 'password2']

    # Validación de las contraseñas
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")  # Cambiado a password2 para coincidir con UserCreationForm

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data
