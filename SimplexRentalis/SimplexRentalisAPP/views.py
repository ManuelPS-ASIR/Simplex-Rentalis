from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Propiedades
from .forms import UserRegistrationForm

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
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

# Vista personalizada de inicio de sesión (login) para responder en formato JSON
def login_view(request):
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
