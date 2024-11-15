from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from .models import Propiedades, User
from .forms import RegistroForm, ConfiguracionCuentaForm

# Vista para la página de inicio
def index(request):
    propiedades_mas_visitadas = Propiedades.objects.all()[:5]
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })

# Vista para mostrar todas las propiedades
def propiedades(request):
    propiedades = Propiedades.objects.all()
    return render(request, 'SimplexRentalisAPP/propiedades_list.html', {
        'propiedades': propiedades
    })

# Vista para mostrar las propiedades del usuario autenticado
@login_required
def propiedades_usuario(request):
    propiedades = Propiedades.objects.filter(propietario=request.user)
    return render(request, 'SimplexRentalisAPP/propiedades_usuario.html', {
        'propiedades': propiedades
    })

# Vista para el registro de usuario
def register(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Registro exitoso e inicio de sesión automático.',
                    'username': user.username,
                    'avatar_url': user.avatar.url if user.avatar else '',
                })
            else:
                return JsonResponse({'success': False, 'error': {'general': 'Error al autenticar al usuario.'}})
        else:
            errors = {field: error[0].__str__() for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'error': errors}, status=400)

    return render(request, 'registration/registro.html', {'form': RegistroForm()})

# Vista personalizada de inicio de sesión (login) para responder en formato JSON
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user_authenticated = authenticate(request, username=username, password=password)
            if user_authenticated is not None:
                login(request, user_authenticated)
                return JsonResponse({
                    'success': True,
                    'username': user.username,
                    'avatar_url': user.profile.avatar.url if hasattr(user, 'profile') else '',
                })
            else:
                return JsonResponse({'success': False, 'error': {'password': _('Contraseña incorrecta')}})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': {'username': _('El nombre de usuario no existe')}})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

# Vista de cierre de sesión
def logout_view(request):
    logout(request)
    return redirect('index')  # Redirige al usuario a la página principal después de cerrar sesión

# Vista para propiedades de usuario (ya definida anteriormente)
@login_required
def propiedades_usuario(request):
    propiedades = Propiedades.objects.filter(propietario=request.user)
    return render(request, 'propiedades_usuario.html', {
        'propiedades': propiedades
    })

# Vista para la configuración de la cuenta
@login_required
def account_settings(request):
    if request.method == 'POST':
        user = request.user
        form_data = request.POST.copy()

        # Filtrar datos iniciales no modificados
        for field in form_data.keys():
            if field in user.__dict__ and form_data[field] == str(getattr(user, field)):
                form_data.pop(field)

        form = ConfiguracionCuentaForm(form_data, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
                return redirect('settings')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: error[0] for field, error in form.errors.items()}
                return JsonResponse({'success': False, 'error': errors}, status=400)
            else:
                messages.error(request, 'Por favor, corrige los errores a continuación.')

    else:
        form = ConfiguracionCuentaForm(instance=request.user)

    return render(request, 'SimplexRentalisAPP/settings.html', {'form': form})

# Vista para cambiar la contraseña
@login_required
def password_change_view(request):
    # Lógica para cambiar la contraseña
    return render(request, 'password_change.html')

# Vista para eliminar la cuenta
@login_required
def delete_account_view(request):
    # Lógica para eliminar la cuenta
    return render(request, 'delete_account.html')
