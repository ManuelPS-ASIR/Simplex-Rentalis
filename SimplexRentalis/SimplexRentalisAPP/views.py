from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Propiedades
from .forms import RegistroForm

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
            # Guardar el nuevo usuario en la base de datos
            user = form.save()

            # Autenticar al usuario con el nombre de usuario y la contraseña
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')  # Contraseña proporcionada en el formulario
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Si el usuario se autentica correctamente, iniciar sesión automáticamente
                login(request, user)

                # Responder con datos del usuario ya autenticado
                return JsonResponse({
                    'success': True,
                    'message': 'Registro exitoso e inicio de sesión automático.',
                    'username': user.username,
                    'avatar_url': user.avatar.url if user.avatar else '',  # Si tiene avatar, lo mostramos
                })
            else:
                # Si no se puede autenticar al usuario, enviar un error
                return JsonResponse({'success': False, 'message': 'Error al autenticar al usuario.'})

        else:
            # Si el formulario no es válido, devolver los errores del formulario
            errors = form.errors.as_json()
            return JsonResponse({
                'success': False,
                'error': errors
            }, status=400)

    return render(request, 'registration/registro.html', {'form': RegistroForm()})
# Vista personalizada de inicio de sesión (login) para responder en formato JSON
def login_view(request):
    if request.user.is_authenticated:
        # Si el usuario ya está autenticado, redirigimos a la página principal
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Responder con los datos del usuario en formato JSON
            return JsonResponse({
                'success': True,
                'username': user.username,
                'avatar_url': user.profile.avatar.url if hasattr(user, 'profile') else '',  # Avatar si existe el perfil
            })
        else:
            # Si las credenciales son incorrectas, se responde con un error
            return JsonResponse({'success': False, 'message': 'Credenciales incorrectas'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

# Vista de cierre de sesión
def logout_view(request):
    logout(request)
    return redirect('index')  # Redirige al usuario a la página principal después de cerrar sesión

# Vista para propiedades de usuario
@login_required
def propiedades_usuario(request):
    propiedades = Propiedades.objects.filter(propietario=request.user)
    return render(request, 'propiedades_usuario.html', {
        'propiedades': propiedades
    })

# Vista para la configuración de la cuenta
def account_settings(request):
    return render(request, 'SimplexRentalisAPP/account_settings.html')
