from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from .models import Propiedades, User, Galeria
from .forms import RegistroForm, ConfiguracionCuentaForm

# Página de inicio
def index(request):
    propiedades_mas_visitadas = Propiedades.objects.all()[:5]
    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mas_visitadas': propiedades_mas_visitadas
    })

from django.db.models import Case, When, Value

def propiedades(request):
    propiedades = Propiedades.objects.prefetch_related('gallery_images').filter(en_mantenimiento=False)

    for propiedad in propiedades:
        # Intentar obtener la imagen de portada o la primera imagen asociada
        portada = propiedad.gallery_images.filter(portada=True).order_by('id').first()
        if not portada:
            portada = propiedad.gallery_images.order_by('id').first()

        # Si no hay imágenes, asignar una URL predeterminada
        propiedad.portada = portada.imagen.url if portada else "/static/images/default_property.jpg"

    return render(request, 'propiedades.html', {'propiedades': propiedades})

# Mostrar propiedades del usuario autenticado
@login_required
def propiedades_usuario(request):
    propiedades = Propiedades.objects.filter(propietario=request.user)
    return render(request, 'SimplexRentalisAPP/propiedades_usuario.html', {
        'propiedades': propiedades
    })

# Registro de usuario
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

# Inicio de sesión personalizado
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

# Cierre de sesión
def logout_view(request):
    logout(request)
    return redirect('index')

# Configuración de la cuenta
@login_required
def account_settings(request):
    if request.method == 'POST':
        user = request.user
        form_data = request.POST.copy()

        # Filtrar datos no modificados
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

# Agregar propiedad
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Propiedades, Galeria

@login_required
def agregar_propiedad(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        precio_noche = request.POST.get('precio_noche', '0')
        capacidad_maxima = request.POST.get('capacidad_maxima', '0')
        permite_mascotas = 'permite_mascotas' in request.POST
        en_mantenimiento = 'en_mantenimiento' in request.POST
        portada = request.POST.get('portada', '0')  # Índice de la imagen de portada

        try:
            precio_noche = float(precio_noche)
            capacidad_maxima = int(capacidad_maxima)
        except ValueError:
            messages.error(request, "Valores inválidos.")
            return redirect('agregar_propiedad')

        # Verificar si ya existe una propiedad con la misma dirección para el usuario
        if Propiedades.objects.filter(direccion=direccion, propietario=request.user).exists():
            messages.error(request, "Ya existe una propiedad con esta dirección.")
            return redirect('agregar_propiedad')

        # Crear la nueva propiedad
        propiedad = Propiedades.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            precio_noche=precio_noche,
            permite_mascotas=permite_mascotas,
            en_mantenimiento=en_mantenimiento,
            capacidad_maxima=capacidad_maxima,
            propietario=request.user
        )

        # Manejo de imágenes
        if 'imagenes' in request.FILES:
            images = request.FILES.getlist('imagenes')
            if not (5 <= len(images) <= 15):
                messages.error(request, "Debes subir entre 5 y 15 imágenes.")
                propiedad.delete()  # Eliminar propiedad creada si hay un error
                return redirect('agregar_propiedad')

            # Guardar las imágenes y manejar la portada
            for index, image in enumerate(images):
                nueva_imagen = Galeria.objects.create(propiedad=propiedad, imagen=image)
                # Establecer la portada según el índice enviado
                if str(index) == portada:
                    nueva_imagen.portada = True
                    nueva_imagen.save()

            # Si ninguna imagen fue marcada como portada, establecer la primera como predeterminada
            if not any(img.portada for img in Galeria.objects.filter(propiedad=propiedad)):
                primera_imagen = Galeria.objects.filter(propiedad=propiedad).first()
                if primera_imagen:
                    primera_imagen.portada = True
                    primera_imagen.save()
        else:
            messages.error(request, "Debes subir imágenes.")
            propiedad.delete()  # Eliminar la propiedad si no hay imágenes
            return redirect('agregar_propiedad')

        # Redirigir a "Mis Propiedades" después de agregar la propiedad
        messages.success(request, "Propiedad agregada exitosamente.")
        return redirect('propiedades_usuario')  # Cambiar 'mis_propiedades' por el nombre correcto de tu vista de "Mis Propiedades"

    return render(request, 'SimplexRentalisAPP/agregar_propiedad.html')


from django.db.models import Min

@login_required
def agregar_imagenes(request, propiedad_id):
    propiedad = get_object_or_404(Propiedades, id=propiedad_id)

    if request.method == "POST":
        images = request.FILES.getlist('images')

        for image in images:
            Galeria.objects.create(propiedad=propiedad, imagen=image)

        # Asignar portada solo si no existe una portada asignada
        if not Galeria.objects.filter(propiedad=propiedad, portada=True).exists():
            # Seleccionar la imagen más antigua según el campo de creación
            primera_imagen = Galeria.objects.filter(propiedad=propiedad).annotate(
                min_fecha=Min('id')  # Suponiendo que `id` crece de manera incremental
            ).order_by('min_fecha').first()

            if primera_imagen:
                primera_imagen.portada = True
                primera_imagen.save()

        return JsonResponse({"success": True, "message": "Imágenes cargadas correctamente."})

    return render(request, "SimplexRentalisAPP/agregar_imagenes.html", {'propiedad': propiedad})

# Vista detallada de una propiedad
def propiededad_detallada(request, propiedad_id):
    propiedad = get_object_or_404(Propiedades, pk=propiedad_id)
    return render(request, 'SimplexRentalisAPP/propiededad_detallada.html', {
        'propiedad': propiedad
    })
# Vista para eliminar la cuenta
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('index')  # redirigir a una página adecuada tras la eliminación

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('settings')  # Redirige a la configuración de cuenta o cualquier otra vista
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'SimplexRentalisAPP/password_change.html', {'form': form})

from .forms import PropiedadForm

def editar_propiedad(request, pk):
    # Obtener la propiedad a editar
    propiedad = get_object_or_404(Propiedades, pk=pk)

    # Si el método de la solicitud es POST, significa que el formulario fue enviado
    if request.method == 'POST':
        form = PropiedadForm(request.POST, instance=propiedad)
        
        # Verificamos si el formulario es válido
        if form.is_valid():
            # Guardamos los cambios de la propiedad
            form.save()
            # Redirigimos a la vista de detalles de la propiedad (puedes cambiar la URL si es necesario)
            return redirect('propiedad_detallada', pk=propiedad.pk)
    else:
        # Si es una solicitud GET, prellenamos el formulario con los datos de la propiedad
        form = PropiedadForm(instance=propiedad)

    # Renderizamos el formulario en una plantilla
    return render(request, 'editar_propiedad.html', {'form': form, 'propiedad': propiedad})

from django.shortcuts import get_object_or_404, redirect
from .models import Propiedades

def eliminar_propiedad(request, pk):
    # Obtener la propiedad a eliminar
    propiedad = get_object_or_404(Propiedades, pk=pk)
    
    # Verificar si el usuario actual es el propietario de la propiedad
    if propiedad.propietario == request.user:
        propiedad.delete()
        # Redirigir al listado de propiedades
        return redirect('mis_propiedades')
    else:
        # Si el usuario no es el propietario, redirigir con un mensaje de error o simplemente denegar
        return redirect('mis_propiedades')  # Puedes personalizar el mensaje de error o la redirección
