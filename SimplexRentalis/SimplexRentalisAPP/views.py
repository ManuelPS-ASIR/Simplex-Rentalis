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

    return render(request, 'SimplexRentalisAPP/propiedades_list.html', {'propiedades': propiedades})

# Mostrar propiedades del usuario autenticado
@login_required
def propiedades_usuario(request):
    propiedades = Propiedades.objects.filter(propietario=request.user)
    estrellas = range(1, 6)
    for propiedad in propiedades:
        portada = propiedad.gallery_images.filter(portada=True).first()
        if not portada:
            portada = propiedad.gallery_images.first()
        propiedad.portada = portada
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

        print(f"Datos recibidos: nombre={nombre}, descripcion={descripcion}, direccion={direccion}, "
              f"precio_noche={precio_noche}, capacidad_maxima={capacidad_maxima}, permite_mascotas={permite_mascotas}, "
              f"en_mantenimiento={en_mantenimiento}, portada={portada}")  # Mensaje de depuración

        try:
            precio_noche = float(precio_noche)
            capacidad_maxima = int(capacidad_maxima)
        except ValueError:
            messages.error(request, "Valores inválidos.")
            print("Error: Valores inválidos para precio_noche o capacidad_maxima.")  # Mensaje de depuración
            return redirect('agregar_propiedad')

        # Verificar si ya existe una propiedad con la misma dirección para el usuario
        if Propiedades.objects.filter(direccion=direccion, propietario=request.user).exists():
            messages.error(request, "Ya existe una propiedad con esta dirección.")
            print(f"Error: Ya existe una propiedad con la dirección {direccion} para el usuario {request.user}.")  # Mensaje de depuración
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

        print(f"Propiedad creada: {propiedad}")  # Mensaje de depuración

        # Manejo de imágenes
        if 'imagenes' in request.FILES:
            images = request.FILES.getlist('imagenes')
            if not (5 <= len(images) <= 15):
                messages.error(request, "Debes subir entre 5 y 15 imágenes.")
                propiedad.delete()  # Eliminar propiedad creada si hay un error
                print("Error: Número de imágenes no válido.")  # Mensaje de depuración
                return redirect('agregar_propiedad')

            # Guardar las imágenes y manejar la portada
            for index, image in enumerate(images):
                nueva_imagen = Galeria.objects.create(propiedad=propiedad, imagen=image)
                print(f"Imagen guardada: {nueva_imagen}")  # Mensaje de depuración
                # Establecer la portada según el índice enviado
                if str(index) == portada:
                    nueva_imagen.portada = True
                    nueva_imagen.save()
                    print(f"Portada establecida: {nueva_imagen}")  # Mensaje de depuración

            # Si ninguna imagen fue marcada como portada, establecer la primera como predeterminada
            if not any(img.portada for img in Galeria.objects.filter(propiedad=propiedad)):
                primera_imagen = Galeria.objects.filter(propiedad=propiedad).first()
                if primera_imagen:
                    primera_imagen.portada = True
                    primera_imagen.save()
                    print(f"Portada predeterminada: {primera_imagen}")  # Mensaje de depuración
        else:
            messages.error(request, "Debes subir imágenes.")
            propiedad.delete()  # Eliminar la propiedad si no hay imágenes
            print("Error: No se subieron imágenes.")  # Mensaje de depuración
            return redirect('agregar_propiedad')

        # Redirigir a "Mis Propiedades" después de agregar la propiedad
        messages.success(request, "Propiedad agregada exitosamente.")
        print("Propiedad agregada exitosamente.")  # Mensaje de depuración
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
from django.views.generic.detail import DetailView
from .models import Propiedades, Galeria

class DetallePropiedadView(DetailView):
    model = Propiedades
    template_name = 'SimplexRentalisAPP/propiedad_detallada.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        propiedad = self.get_object()
        context['imagen_portada'] = Galeria.objects.filter(propiedad=propiedad, portada=True).first()
        context['imagenes'] = Galeria.objects.filter(propiedad=propiedad)
        return context

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
    propiedad = get_object_or_404(Propiedades, pk=pk)
    
    if request.method == 'POST':
        propiedad.delete()  # Eliminar la propiedad
        return redirect('propiedades_usuario')  # Redirigir de nuevo a la lista de propiedades
    
    return render(request, 'confirmar_eliminacion.html', {'propiedad': propiedad})

from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Propiedades  # Asegúrate de importar el modelo adecuado

@login_required
def cambiar_estado_propietario(request):
    user = request.user
    if request.method == 'POST':
        if user.es_propietario:
            # Eliminar todas las propiedades del usuario
            Propiedades.objects.filter(propietario=user).delete()
        
        # Cambiar el estado de propietario
        user.es_propietario = not user.es_propietario
        user.save()
        
        estado = "activado" if user.es_propietario else "desactivado"
        messages.success(request, f"Tu estado de propietario ha sido {estado}.")
        
        # Redirigir según el nuevo estado
        if user.es_propietario:
            return redirect('agregar_propiedad')  # Redirige a la vista de agregar propiedad
        else:
            return redirect('settings')  # Redirige a la vista de configuración o preferida
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


from django.http import JsonResponse
import requests

def autocompletar_direcciones(request):
    query = request.GET.get('query', '')  # Obtener la consulta parcial del usuario
    if not query:
        return JsonResponse({"error": "La consulta está vacía"}, status=400)

    url = "https://photon.komoot.io/api/"
    params = {
        "q": query,
        "limit": 5,
        "lang": "es"  # Idioma para las sugerencias
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        sugerencias = [
            {
                "direccion": feature["properties"]["name"],
                "detalle": feature["properties"].get("city", ""),
                "provincia": feature["properties"].get("state", ""),
                "pais": feature["properties"].get("country", ""),
                "latitud": feature["geometry"]["coordinates"][1],
                "longitud": feature["geometry"]["coordinates"][0],
            }
            for feature in data["features"]
        ]
        return JsonResponse(sugerencias, safe=False)
    else:
        return JsonResponse({"error": "Error al contactar con Photon"}, status=500)



from django.shortcuts import render, get_object_or_404, redirect
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
import json
from .models import Propiedades, Reservas, Identidades
from .forms import ReservaForm, IdentidadForm

# Vista para alquilar una propiedad
def alquilar_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedades, id=propiedad_id)
    form_reserva = ReservaForm()
    form_identidad = IdentidadForm()

    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST)
        form_identidad = IdentidadForm(request.POST)

        if form_reserva.is_valid() and form_identidad.is_valid():
            reserva = form_reserva.save(commit=False)
            reserva.propiedad = propiedad
            reserva.usuario = request.user
            reserva.save()

            identidad = form_identidad.save(commit=False)
            identidad.reserva = reserva
            identidad.save()

            form_reserva.save_m2m()  # Guardar relaciones many-to-many

            return redirect('reserva_exitosa')

    # Obtener todas las fechas no disponibles basadas en las reservas
    reservas = propiedad.reservas.all()
    fechas_no_disponibles = []
    for reserva in reservas:
        rango = [reserva.fecha_inicio + timedelta(days=i) for i in range((reserva.fecha_fin - reserva.fecha_inicio).days + 1)]
        fechas_no_disponibles.extend(rango)

    fechas_no_disponibles_json = json.dumps([fecha.strftime('%Y-%m-%d') for fecha in fechas_no_disponibles], cls=DjangoJSONEncoder)

    return render(request, 'SimplexRentalisAPP/alquilar_propiedad.html', {
        'propiedad': propiedad,
        'form_reserva': form_reserva,
        'form_identidad': form_identidad,
        'fechas_no_disponibles_json': fechas_no_disponibles_json,
    })

# Vista para mostrar el mensaje de reserva exitosa
def reserva_exitosa_view(request):
    return render(request, 'SimplexRentalisAPP/reserva_exitosa.html')
