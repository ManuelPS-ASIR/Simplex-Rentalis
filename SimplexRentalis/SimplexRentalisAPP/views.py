from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from .models import Propiedades, User, Galeria
from .forms import RegistroForm, ConfiguracionCuentaForm
from .models import Propiedades, Galeria

# Vista para la página de inicio
def index(request):
    propiedades_mas_visitadas = Propiedades.objects.all()[:5]
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })

# Vista para mostrar todas las propiedades
def propiedades(request):
    propiedades = Propiedades.objects.prefetch_related(
        'gallery_images'
    ).filter(en_mantenimiento=False)

    for propiedad in propiedades:
        portada = propiedad.gallery_images.filter(portada=True).first()
        propiedad.portada = portada.imagen.url if portada else None

    return render(request, 'propiedades.html', {'propiedades': propiedades})


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
            # Imprime los errores del formulario para depuración
            print("Errores del formulario:", form.errors)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Manejo de errores para solicitudes AJAX
                errors = {field: error[0] for field, error in form.errors.items()}
                return JsonResponse({'success': False, 'error': errors}, status=400)
            else:
                # Manejo de errores para solicitudes normales
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
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('index')  # redirigir a una página adecuada tras la eliminación


@login_required
def agregar_propiedad(request):
    if request.method == 'POST':
        # Guardamos los datos recibidos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        precio_noche = request.POST.get('precio_noche')
        permite_mascotas = 'permite_mascotas' in request.POST
        en_mantenimiento = 'en_mantenimiento' in request.POST
        capacidad_maxima = request.POST.get('capacidad_maxima')

        # Verificamos si ya existe una propiedad con la misma dirección y propietario
        if Propiedades.objects.filter(direccion=direccion, propietario=request.user).exists():
            # Si ya existe, puedes enviar un error o mensaje
            messages.error(request, "Ya tienes una propiedad con esta dirección.")
            return redirect('agregar_propiedad')  # O la URL adecuada

        # Si no existe, creamos la propiedad
        propiedad = Propiedades.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            precio_noche=precio_noche,
            permite_mascotas=permite_mascotas,
            en_mantenimiento=en_mantenimiento,
            capacidad_maxima=capacidad_maxima,
            propietario=request.user  # Asociamos al propietario
        )

        # Manejar las imágenes subidas
        if 'imagenes' in request.FILES:
            images = request.FILES.getlist('imagenes')
            for image in images:
                Galeria.objects.create(propiedad=propiedad, imagen=image)

            # Opcional: Marcar la primera imagen como portada
            if images:
                portada_imagen = Galeria.objects.filter(propiedad=propiedad).first()
                portada_imagen.portada = True
                portada_imagen.save()

        # Pasar las imágenes al template
        imagenes = Galeria.objects.filter(propiedad=propiedad)

        return render(request, 'SimplexRentalisAPP/agregar_propiedad.html', {'imagenes': imagenes})

    else:
        return render(request, 'SimplexRentalisAPP/propiedades_usuario.html')


# Vista para agregar imágenes adicionales a una propiedad
@login_required
def agregar_imagenes(request, propiedad_id):
    propiedad = Propiedades.objects.get(id=propiedad_id)

    if request.method == "POST":
        images = request.FILES.getlist('images')  # Obtener las imágenes desde el formulario

        for image in images:
            Galeria.objects.create(propiedad=propiedad, image=image)

        # Opcional: Marcar la primera imagen como la imagen principal (portada)
        if images:
            gallery = Galeria.objects.filter(propiedad=propiedad).first()
            gallery.portada = True
            gallery.save()

        return JsonResponse({"success": True, "message": "Imágenes cargadas correctamente."})

    return render(request, "SimplexRentalisAPP/agregar_imagenes.html", {'propiedad': propiedad})

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Propiedades

# Vista para mostrar los detalles de una propiedad
def propiededad_detallada(request, propiedad_id):
    propiedad = get_object_or_404(Propiedades, pk=propiedad_id)
    return render(request, 'SimplexRentalisAPP/propiededad_detallada.html', {
        'propiedad': propiedad
    })
