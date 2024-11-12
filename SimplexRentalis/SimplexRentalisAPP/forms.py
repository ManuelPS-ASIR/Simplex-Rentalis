from django import forms
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario
User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    # Campos del formulario
    contraseña = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    contraseña2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    telefono = forms.CharField(max_length=15, label="Teléfono")
    genero = forms.ChoiceField(choices=[('male', 'Masculino'), ('female', 'Femenino'), ('other', 'Otro')], label="Género")
    fecha_nacimiento = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2100)), label="Fecha de nacimiento")
    avatar = forms.ImageField(required=False, label="Imagen de perfil (Opcional)")

    class Meta:
        model = User
        # Campos que se mostrarán en el formulario
        fields = ['username', 'email', 'telefono', 'genero', 'fecha_nacimiento', 'avatar']
    
    def clean_contraseña2(self):
        cd = self.cleaned_data
        if cd['contraseña'] != cd['contraseña2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['contraseña2']
