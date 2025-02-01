from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.contrib import messages
from .models import Propiedades, User, Galeria
from .forms import RegistroForm, ConfiguracionCuentaForm

# Página de inicio
from django.shortcuts import render
from .models import Propiedades
from random import sample

def index(request):
    all_properties = Propiedades.objects.order_by('-calificacion')[:100]

    if len(all_properties) < 8:
        propiedades_mejor_calificadas = []  # Lista vacía si no hay suficientes propiedades
    else:
        propiedades_mejor_calificadas = sample(list(all_properties), 8)

        for propiedad in propiedades_mejor_calificadas:
            portada = propiedad.gallery_images.filter(portada=True).first()
            propiedad.portada = portada if portada else None  # Imagen predeterminada opcional

    return render(request, 'SimplexRentalisAPP/index.html', {
        'propiedades_mejor_calificadas': propiedades_mejor_calificadas,
        'no_hay_propiedades': len(all_properties) < 8  # Variable para el template
    })

from django.db.models import Q, Min, Max
from django.shortcuts import render
from .models import Propiedades
from .forms import FiltroPropiedadesForm

def propiedades(request):
    query = request.GET.get('q')
    direccion = request.GET.get('direccion')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    calificacion = request.GET.get('calificacion')
    permite_mascotas = request.GET.get('permite_mascotas')
    capacidad_maxima = request.GET.get('capacidad_maxima')

    precio_minimo = Propiedades.objects.aggregate(min_precio=Min('precio_noche'))['min_precio'] or 0
    precio_maximo = Propiedades.objects.aggregate(max_precio=Max('precio_noche'))['max_precio'] or 10000

    form = FiltroPropiedadesForm(request.GET)
    propiedades = Propiedades.objects.prefetch_related('gallery_images').filter(en_mantenimiento=False)

    if query:
        propiedades = propiedades.filter(
            Q(nombre__icontains=query) | Q(direccion__icontains=query)
        )

    if form.is_valid():
        if direccion:
            propiedades = propiedades.filter(direccion__icontains=direccion)
        if precio_min:
            propiedades = propiedades.filter(precio_noche__gte=precio_min)
        if precio_max:
            propiedades = propiedades.filter(precio_noche__lte=precio_max)
        if calificacion:
            propiedades = propiedades.filter(calificacion__gte=int(calificacion))
        if permite_mascotas:
            propiedades = propiedades.filter(permite_mascotas=(permite_mascotas == 'True'))
        if capacidad_maxima:
            propiedades = propiedades.filter(capacidad_maxima__gte=capacidad_maxima)  # Usar `gte` para capacidad máxima

    for propiedad in propiedades:
        portada = propiedad.gallery_images.filter(portada=True).order_by('id').first()
        if not portada:
            portada = propiedad.gallery_images.order_by('id').first()
        propiedad.portada = portada.imagen.url if portada else "/static/images/default_property.jpg"

    if 'precio_max' not in request.GET:
        form.fields['precio_max'].initial = precio_maximo
    if 'precio_min' not in request.GET:
        form.fields['precio_min'].initial = precio_minimo

    context = {
        'propiedades': propiedades,
        'form': form,
        'precio_minimo': precio_minimo,
        'precio_maximo': precio_maximo,
        'query': query
    }

    return render(request, 'SimplexRentalisAPP/propiedades_list.html', context)




#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Propiedades, Direcciones, Galeria  # Asegúrate de importar todos los modelos necesarios

@login_required
def agregar_propiedad(request):
    if request.method == 'POST':
        # Datos de la propiedad
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio_noche = request.POST.get('precio_noche', '0')
        capacidad_maxima = request.POST.get('capacidad_maxima', '0')
        permite_mascotas = 'permite_mascotas' in request.POST
        en_mantenimiento = 'en_mantenimiento' in request.POST
        portada = request.POST.get('portada', '0')  # Índice de la imagen de portada

        # Datos de la dirección (asegúrate de que el formulario envíe estos campos)
        calle = request.POST.get('calle')
        numero_casa = request.POST.get('numero_casa')
        numero_puerta = request.POST.get('numero_puerta')
        codigo_postal = request.POST.get('codigo_postal')
        ciudad = request.POST.get('ciudad')
        co_autonoma = request.POST.get('co_autonoma')
        provincia = request.POST.get('provincia')
        pais = request.POST.get('pais')

        # Mensaje de depuración
        print(f"Datos recibidos: nombre={nombre}, descripcion={descripcion}, precio_noche={precio_noche}, "
              f"capacidad_maxima={capacidad_maxima}, permite_mascotas={permite_mascotas}, "
              f"en_mantenimiento={en_mantenimiento}, portada={portada}")
        print(f"Datos de dirección: calle={calle}, numero_casa={numero_casa}, numero_puerta={numero_puerta}, "
              f"codigo_postal={codigo_postal}, ciudad={ciudad}, co_autonoma={co_autonoma}, "
              f"provincia={provincia}, pais={pais}")

        # Conversión de valores numéricos
        try:
            precio_noche = float(precio_noche)
            capacidad_maxima = int(capacidad_maxima)
        except ValueError:
            messages.error(request, "Valores inválidos para precio o capacidad.")
            print("Error: Valores inválidos para precio_noche o capacidad_maxima.")
            return redirect('agregar_propiedad')

        # Crear la instancia de Direcciones con los datos recibidos
        try:
            direccion_instance = Direcciones.objects.create(
                calle=calle,
                numero_casa=numero_casa,
                numero_puerta=numero_puerta,
                codigo_postal=codigo_postal,
                ciudad=ciudad,
                co_autonoma=co_autonoma,
                provincia=provincia,
                pais=pais
            )
            print(f"Dirección creada: {direccion_instance}")
        except ValidationError as e:
            messages.error(request, f"Error en la dirección: {e}")
            print(f"Error al crear la dirección: {e}")
            return redirect('agregar_propiedad')

        # Verificar si ya existe una propiedad con la misma dirección para el usuario
        if Propiedades.objects.filter(direccion=direccion_instance, propietario=request.user).exists():
            messages.error(request, "Ya existe una propiedad con esta dirección.")
            print(f"Error: Ya existe una propiedad con la dirección {direccion_instance} para el usuario {request.user}.")
            return redirect('agregar_propiedad')

        # Crear la nueva propiedad asignando la dirección creada
        propiedad = Propiedades.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion_instance,  # Se asigna la instancia de Direcciones
            precio_noche=precio_noche,
            permite_mascotas=permite_mascotas,
            en_mantenimiento=en_mantenimiento,
            capacidad_maxima=capacidad_maxima,
            propietario=request.user
        )
        print(f"Propiedad creada: {propiedad}")

        # Manejo de imágenes
        if 'imagenes' in request.FILES:
            images = request.FILES.getlist('imagenes')
            if not (5 <= len(images) <= 15):
                messages.error(request, "Debes subir entre 5 y 15 imágenes.")
                propiedad.delete()  # Eliminar la propiedad creada si hay un error
                print("Error: Número de imágenes no válido.")
                return redirect('agregar_propiedad')

            # Guardar las imágenes y manejar la portada
            for index, image in enumerate(images):
                nueva_imagen = Galeria.objects.create(propiedad=propiedad, imagen=image)
                print(f"Imagen guardada: {nueva_imagen}")
                # Establecer la imagen de portada según el índice enviado
                if str(index) == portada:
                    nueva_imagen.portada = True
                    nueva_imagen.save()
                    print(f"Portada establecida: {nueva_imagen}")

            # Si ninguna imagen fue marcada como portada, establecer la primera como predeterminada
            if not any(img.portada for img in Galeria.objects.filter(propiedad=propiedad)):
                primera_imagen = Galeria.objects.filter(propiedad=propiedad).first()
                if primera_imagen:
                    primera_imagen.portada = True
                    primera_imagen.save()
                    print(f"Portada predeterminada: {primera_imagen}")
        else:
            messages.error(request, "Debes subir imágenes.")
            propiedad.delete()  # Eliminar la propiedad si no hay imágenes
            print("Error: No se subieron imágenes.")
            return redirect('agregar_propiedad')

        # Actualizar el estado del usuario a propietario si no lo es
        if not request.user.es_propietario:
            request.user.es_propietario = True
            request.user.save()
            messages.success(request, "Tu estado de propietario ha sido activado automáticamente.")
            print("Estado de propietario activado automáticamente para el usuario.")

        # Redirigir a "Mis Propiedades" después de agregar la propiedad
        messages.success(request, "Propiedad agregada exitosamente.")
        print("Propiedad agregada exitosamente.")
        return redirect('propiedades_usuario')  # Asegúrate de que el nombre de la vista sea el correcto

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

from django.views.generic.detail import DetailView
from .models import Propiedades, Galeria

class DetallePropiedadView(DetailView):
    model = Propiedades
    template_name = 'SimplexRentalisAPP/propiedad_detallada.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        propiedad = self.get_object()
        
        # Definimos la variable permite_opinar_sin_reserva
        permite_opinar_sin_reserva = True  # Puedes cambiar a False para desactivar esta opción
        user_has_reservation = False  # Aquí deberías añadir la lógica real para comprobar la reserva del usuario

        context['imagen_portada'] = Galeria.objects.filter(propiedad=propiedad, portada=True).first()
        context['imagenes'] = Galeria.objects.filter(propiedad=propiedad)
        context['permite_opinar_sin_reserva'] = permite_opinar_sin_reserva
        context['user_has_reservation'] = user_has_reservation
        
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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import PropiedadForm
from .models import Propiedades, Galeria

def editar_propiedad(request, pk):
    propiedad = get_object_or_404(Propiedades, pk=pk)
    # Verificación de propietario 
    if propiedad.propietario != request.user: 
        return render(request, 'SimplexRentalisAPP/403.html')
    imagenes = Galeria.objects.filter(propiedad=propiedad)
    imagen_portada = imagenes.filter(portada=True).first() if imagenes else None

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        precio_noche = request.POST.get('precio_noche', '0')
        capacidad_maxima = request.POST.get('capacidad_maxima', '0')
        permite_mascotas = 'permite_mascotas' in request.POST
        en_mantenimiento = 'en_mantenimiento' in request.POST

        print(f"Datos recibidos: nombre={nombre}, descripcion={descripcion}, direccion={direccion}, "
              f"precio_noche={precio_noche}, capacidad_maxima={capacidad_maxima}, permite_mascotas={permite_mascotas}, "
              f"en_mantenimiento={en_mantenimiento}")  # Mensaje de depuración

        try:
            precio_noche = float(precio_noche)
            capacidad_maxima = int(capacidad_maxima)
        except ValueError:
            messages.error(request, "Valores inválidos.")
            print("Error: Valores inválidos para precio_noche o capacidad_maxima.")  # Mensaje de depuración
            return redirect('editar_propiedad', pk=pk)

        # Verificar si ya existe una propiedad con la misma dirección para el usuario
        if Propiedades.objects.filter(direccion=direccion, propietario=request.user).exclude(pk=pk).exists():
            messages.error(request, "Ya existe una propiedad con esta dirección.")
            print(f"Error: Ya existe una propiedad con la dirección {direccion} para el usuario {request.user}.")  # Mensaje de depuración
            return redirect('editar_propiedad', pk=pk)

        # Actualizar la propiedad
        propiedad.nombre = nombre
        propiedad.descripcion = descripcion
        propiedad.direccion = direccion
        propiedad.precio_noche = precio_noche
        propiedad.capacidad_maxima = capacidad_maxima
        propiedad.permite_mascotas = permite_mascotas
        propiedad.en_mantenimiento = en_mantenimiento
        propiedad.save()
        print(f"Propiedad actualizada: {propiedad}")  # Mensaje de depuración

        # Manejo de imágenes
        nuevas_imagenes = request.FILES.getlist('imagenes')
        total_imagenes = imagenes.count() + len(nuevas_imagenes)

        if not (5 <= total_imagenes <= 15):
            messages.error(request, "Debes tener entre 5 y 15 imágenes en total (existentes + nuevas).")
            print("Error: Número de imágenes no válido.")  # Mensaje de depuración
            return redirect('editar_propiedad', pk=pk)

        # Eliminar las imágenes seleccionadas para eliminar
        imagenes_eliminar = request.POST.getlist('imagenes_eliminar')
        if imagenes_eliminar:
            Galeria.objects.filter(id__in=imagenes_eliminar).delete()
            print(f"Imágenes eliminadas: {imagenes_eliminar}")  # Mensaje de depuración

        # Guardar las nuevas imágenes
        for image in nuevas_imagenes:
            nueva_imagen = Galeria.objects.create(propiedad=propiedad, imagen=image)
            print(f"Imagen guardada: {nueva_imagen}")  # Mensaje de depuración

        # Subir nueva imagen de portada y eliminar la anterior
        if 'portada_imagen' in request.FILES:
            nueva_portada = request.FILES['portada_imagen']
            if imagen_portada:
                imagen_portada.delete()
            nueva_imagen_portada = Galeria.objects.create(propiedad=propiedad, imagen=nueva_portada, portada=True)
            print(f"Portada actualizada: {nueva_imagen_portada}")  # Mensaje de depuración

        # Redirigir a los detalles de la propiedad después de actualizarla
        messages.success(request, "Propiedad actualizada exitosamente.")
        print("Propiedad actualizada exitosamente.")  # Mensaje de depuración
        return redirect('propiedad_detallada', pk=propiedad.pk)
    else:
        form = PropiedadForm(instance=propiedad)

    return render(request, 'SimplexRentalisAPP/editar_propiedad.html', {
        'form': form,
        'propiedad': propiedad,
        'imagenes': imagenes,
        'imagen_portada': imagen_portada,
        'precio_noche': propiedad.precio_noche,
        'direccion': propiedad.direccion,
    })


from django.shortcuts import get_object_or_404, redirect
from .models import Propiedades

def eliminar_propiedad(request, pk):
    propiedad = get_object_or_404(Propiedades, pk=pk)
    
    if request.method == 'POST':
        propiedad.delete()  # Eliminar la propiedad
        return redirect('propiedades_usuario')  # Redirigir de nuevo a la lista de propiedades
    
    return render(request, 'SimplexRentalisAPP/confirmar_eliminacion.html', {'propiedad': propiedad})
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
# Vista para mostrar el mensaje de reserva exitosa
def reserva_exitosa_view(request):
    return render(request, 'SimplexRentalisAPP/reserva_exitosa.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import IdentidadUsuarioForm  # Asegúrate de tener este formulario configurado para IdentidadUsuario
from .models import IdentidadUsuario

def completar_identidad_usuario(request):
    if request.method == 'POST':
        form = IdentidadUsuarioForm(request.POST)
        if form.is_valid():
            tipo_documento = form.cleaned_data['tipo_documento']
            numero_documento = form.cleaned_data['numero_documento']
            usuario = request.user

            # Verificar si el usuario ya tiene una identidad asociada
            if usuario.identidad_usuario:  # Si el usuario ya tiene una identidad asociada
                # Usar la identidad existente
                identidad = usuario.identidad_usuario
                
                # Solo actualizar si hay cambios en los datos
                if identidad.tipo_documento != tipo_documento or identidad.numero_documento != numero_documento:
                    identidad.tipo_documento = tipo_documento
                    identidad.numero_documento = numero_documento
                    identidad.save()
                    messages.success(request, "Tu identidad ha sido actualizada correctamente.")
                else:
                    messages.info(request, "Los datos de identidad son los mismos. No se realizaron cambios.")
            else:
                # Si no tiene una identidad asociada, crear una nueva
                identidad = form.save(commit=False)
                identidad.usuario = usuario  # Asociar la identidad al usuario autenticado
                identidad.save()

                # Actualizar el campo identidad en el modelo User (si es necesario)
                usuario.identidad_usuario = identidad
                usuario.save()

                messages.success(request, "Tu identidad ha sido guardada correctamente.")

            # Redirigir a la URL almacenada en la sesión o al perfil por defecto
            next_url = request.session.pop('next_url', 'perfil')
            return redirect(next_url)
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            print(form.errors)  # Mensaje de depuración para ver los errores del formulario
    else:
        form = IdentidadUsuarioForm()

    return render(request, 'SimplexRentalisAPP/completar_identidad.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from .models import Propiedades, IdentidadReserva, Reservas, ReservaPersona
from .forms import ReservaForm, IdentidadPersonaForm
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

@login_required
def alquilar_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedades, id=propiedad_id)

    # Obtener la identidad del usuario autenticado para autoprellenar el formulario
    identidad_usuario = request.user.identidad_usuario if hasattr(request.user, 'identidad_usuario') else None

    # Verificar si el usuario tiene una identidad asociada, si no redirigir a completar_identidad
    if not identidad_usuario:
        messages.warning(request, "Debes completar tu identidad antes de realizar una reserva.")
        request.session['next_url'] = request.path
        return redirect('completar_identidad_usuario')  # Asegúrate de que la URL name es correcta

    # Inicializar formulario de IdentidadPersona con los datos de identidad_usuario sin modificarla
    initial_data = {
        'tipo_documento': identidad_usuario.tipo_documento,
        'numero_documento': identidad_usuario.numero_documento,
        'fecha_expedicion': identidad_usuario.fecha_expedicion,
        'primer_apellido': identidad_usuario.primer_apellido,
        'segundo_apellido': identidad_usuario.segundo_apellido,
        'nombre': identidad_usuario.nombre,
        'sexo': identidad_usuario.sexo,
    }

    IdentidadFormSet = modelformset_factory(IdentidadReserva, form=IdentidadPersonaForm, extra=0)

    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST)
        form_identidad = IdentidadPersonaForm(request.POST)
        formset_identidades = IdentidadFormSet(request.POST, queryset=IdentidadReserva.objects.none(), prefix='acompanante')

        # Asignar la propiedad al formulario antes de validar
        form_reserva.instance.propiedad = propiedad

        if form_reserva.is_valid():
            reserva = form_reserva.save(commit=False)
            reserva.usuario = request.user  # Relacionar la reserva con el usuario autenticado
            reserva.propiedad = propiedad
            reserva.fecha_inicio = datetime.combine(reserva.fecha_inicio, datetime.min.time())
            reserva.fecha_fin = datetime.combine(reserva.fecha_fin, datetime.min.time())


            # Verificar si hay reservas existentes en el mismo rango de fechas
            reservas_existentes = Reservas.objects.filter(
                propiedad=propiedad,
                fecha_inicio__lt=reserva.fecha_fin,
                fecha_fin__gt=reserva.fecha_inicio
            ).exclude(id=reserva.id)

            if reservas_existentes.exists():
                mensajes_reservas = [f"Reserva {r.id} desde {r.fecha_inicio} hasta {r.fecha_fin}" for r in reservas_existentes]
                print("Reservas existentes en el rango de fechas seleccionado:", mensajes_reservas)
                messages.error(request, f"La propiedad ya tiene una reserva en el rango de fechas seleccionado: {mensajes_reservas}")
            else:
                try:
                    reserva.full_clean()  # Validar la reserva antes de guardarla
                    reserva.save()  # Guardar la reserva

                    # Crear una instancia de IdentidadReserva basada en identidad_usuario para ReservaPersona
                    nueva_identidad_reserva = IdentidadReserva.objects.create(
                        tipo_documento=identidad_usuario.tipo_documento,
                        numero_documento=identidad_usuario.numero_documento,
                        fecha_expedicion=identidad_usuario.fecha_expedicion,
                        primer_apellido=identidad_usuario.primer_apellido,
                        segundo_apellido=identidad_usuario.segundo_apellido,
                        nombre=identidad_usuario.nombre,
                        sexo=identidad_usuario.sexo
                    )
                    ReservaPersona.objects.create(reserva=reserva, identidad=nueva_identidad_reserva)

                    if form_identidad.is_valid():
                        nueva_identidad = form_identidad.save()

                        if formset_identidades.is_valid():
                            for form in formset_identidades:
                                acompanante = form.save(commit=False)
                                acompanante.save()
                                # Guardar la identidad del acompañante en ReservaPersona
                                ReservaPersona.objects.create(reserva=reserva, identidad=acompanante)

                            messages.success(request, "Reserva realizada con éxito.")
                            return redirect('reserva_exitosa')
                        else:
                            print("Errores en formularios de acompañantes:", formset_identidades.errors)
                            messages.error(request, "Por favor, corrige los errores en los formularios de acompañantes.")
                    else:
                        print("Errores en formulario de identidad del usuario:", form_identidad.errors)
                        messages.error(request, "Por favor, corrige los errores en el formulario de identidad.")
                except ValidationError as e:
                    print("Errores en formulario de reserva:", e.message_dict)
                    messages.error(request, f"Errores en la reserva: {e.message_dict}")
        else:
            print("Errores en formulario de reserva:", form_reserva.errors)
            print("Datos enviados:", form_reserva.cleaned_data)
            messages.error(request, "Por favor, corrige los errores en el formulario de reserva.")
    else:
        form_reserva = ReservaForm(initial={'cantidad_personas': 1})
        form_reserva.fields['cantidad_personas'].widget.attrs['max'] = propiedad.capacidad_maxima
        form_identidad = IdentidadPersonaForm(initial=initial_data)
        formset_identidades = IdentidadFormSet(queryset=IdentidadReserva.objects.none(), prefix='acompanante')

    return render(request, 'SimplexRentalisAPP/alquilar_propiedad.html', {
        'propiedad': propiedad,
        'form_reserva': form_reserva,
        'form_identidad': form_identidad,
        'formset_identidades': formset_identidades,
        'identidad_usuario': identidad_usuario,
    })

from django.shortcuts import render

def reserva_exitosa(request):
    return render(request, 'SimplexRentalisAPP/reserva_exitosa.html')
##################################################################################
# views.py

from django.http import JsonResponse
from .models import Reservas
from datetime import datetime

def obtener_fechas_ocupadas(request, propiedad_id):
    reservas = Reservas.objects.filter(propiedad_id=propiedad_id)
    fechas_ocupadas = []

    for reserva in reservas:
        inicio = reserva.fecha_inicio
        fin = reserva.fecha_fin
        while inicio <= fin:
            fechas_ocupadas.append(inicio.strftime('%Y-%m-%d'))
            inicio += timedelta(days=1)

    return JsonResponse(fechas_ocupadas, safe=False)
##################################################################################
##################################################################################
##################################################################################
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Propiedades, Opiniones, OpinionVote
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def enviar_opinion(request, propiedad_id):
    if request.method == 'POST':
        propiedad = get_object_or_404(Propiedades, id=propiedad_id)
        comentario = request.POST.get('comentario')
        
        if comentario:
            opinion = Opiniones.objects.create(
                propiedad=propiedad,
                usuario=request.user,
                comentario=comentario,
            )
            messages.success(request, 'Tu opinión ha sido enviada con éxito.')
        else:
            messages.error(request, 'Por favor, escribe un comentario.')

    return redirect('propiedad_detallada', pk=propiedad_id)

@csrf_protect
def like_opinion(request, opinion_id):
    opinion = get_object_or_404(Opiniones, id=opinion_id)
    if opinion.usuario == request.user:
        return JsonResponse({'error': 'No puedes votar en tu propia opinión.'}, status=400)

    existing_vote = OpinionVote.objects.filter(opinion=opinion, usuario=request.user).first()
    if existing_vote:
        if existing_vote.voto == 'like':
            existing_vote.delete()
            opinion.likes -= 1
            opinion.save()
            return JsonResponse({'message': 'Has retirado tu "me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})
        elif existing_vote.voto == 'dislike':
            existing_vote.voto = 'like'
            existing_vote.save()
            opinion.dislikes -= 1
            opinion.likes += 1
            opinion.save()
            return JsonResponse({'message': 'Has cambiado tu voto a "me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})
    else:
        OpinionVote.objects.create(opinion=opinion, usuario=request.user, voto='like')
        opinion.likes += 1
        opinion.save()
        return JsonResponse({'message': 'Has votado "me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})

@csrf_protect
def dislike_opinion(request, opinion_id):
    opinion = get_object_or_404(Opiniones, id=opinion_id)
    if opinion.usuario == request.user:
        return JsonResponse({'error': 'No puedes votar en tu propia opinión.'}, status=400)

    existing_vote = OpinionVote.objects.filter(opinion=opinion, usuario=request.user).first()
    if existing_vote:
        if existing_vote.voto == 'dislike':
            existing_vote.delete()
            opinion.dislikes -= 1
            opinion.save()
            return JsonResponse({'message': 'Has retirado tu "no me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})
        elif existing_vote.voto == 'like':
            existing_vote.voto = 'dislike'
            existing_vote.save()
            opinion.likes -= 1
            opinion.dislikes += 1
            opinion.save()
            return JsonResponse({'message': 'Has cambiado tu voto a "no me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})
    else:
        OpinionVote.objects.create(opinion=opinion, usuario=request.user, voto='dislike')
        opinion.dislikes += 1
        opinion.save()
        return JsonResponse({'message': 'Has votado "no me gusta".', 'likes': opinion.likes, 'dislikes': opinion.dislikes})







from django.utils.timezone import now
from .models import Reservas
from datetime import date

@login_required
def mis_reservas(request):
    # Fecha actual definida fuera del bucle
    today = date.today()

    # Obtener las reservas del usuario
    reservas = Reservas.objects.filter(usuario=request.user).select_related('propiedad').prefetch_related('propiedad__galeria__gallery_images')

    # Asignar portada y estado a cada reserva
    for reserva in reservas:
        propiedad = reserva.propiedad
        portada = propiedad.gallery_images.filter(portada=True).first()
        if portada:
            propiedad.portada = portada
        else:
            propiedad.portada = None  # O asignar una imagen predeterminada

        # Determinar el estado de la reserva
        fecha_inicio = reserva.fecha_inicio
        fecha_fin = reserva.fecha_fin

        if fecha_fin < today:
            reserva.estado = 'finalizada'  # Ya finalizó
        elif fecha_inicio <= today <= fecha_fin:
            reserva.estado = 'en_proceso'  # En proceso
        else:
            reserva.estado = 'proxima'  # Próxima

    return render(request, 'SimplexRentalisAPP/mis_reservas.html', {
        'reservas': reservas,
        'today': today  # Pasar la fecha actual
    })








from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Reservas

@login_required
def cancelar_reserva(request, reserva_id):
    if request.method == 'POST':
        # Obtener la reserva solo si el usuario está autenticado y es el propietario
        reserva = get_object_or_404(Reservas, id=reserva_id, usuario=request.user)

        # Verificar si la reserva es cancelable: no se puede cancelar si la fecha de inicio es hoy o en el pasado
        if reserva.fecha_inicio <= now().date():
            return JsonResponse({'success': False, 'message': 'No puedes cancelar una reserva que ya ha comenzado o finalizado.'})

        # Si todo está correcto, eliminar la reserva
        reserva.delete()

        # Respuesta exitosa
        return JsonResponse({'success': True, 'message': 'Tu reserva ha sido cancelada correctamente.'})

    # Si el método no es POST, devolver error de método no permitido
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
















