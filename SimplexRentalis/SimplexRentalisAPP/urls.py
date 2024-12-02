from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Importar vistas de autenticación
from django.conf import settings
from django.conf.urls.static import static
from .views import DetallePropiedadView
from .views import autocompletar_direcciones


urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),  # Usamos la vista personalizada de login
    path('logout/', views.logout_view, name='logout'),  # Usamos nuestra vista personalizada de logout
    path('registro/', views.register, name='register'),
    
    # Modificación en cuenta
    path('settings/', views.account_settings, name='settings'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('cambiar_estado_propietario/', views.cambiar_estado_propietario, name='cambiar_estado_propietario'),


    # Rutas para la aplicación
    path("", views.index, name="index"),
    path('propiedades/', views.propiedades, name='propiedades'),
    
    # Ruta correcta para "Mis Propiedades"
    path('mis_propiedades/', views.propiedades_usuario, name='propiedades_usuario'),
    path('editar_propiedad/<int:pk>/', views.editar_propiedad, name='editar_propiedad'),
    path('eliminar_propiedad/<int:pk>/', views.eliminar_propiedad, name='eliminar_propiedad'),


    
    # Ruta para agregar propiedad
    path('propiedades/agregar/', views.agregar_propiedad, name='agregar_propiedad'),
    path('agregar/', views.agregar_propiedad, name='agregar_propiedad'),
    
    # Ruta para ver detalle de la propiedad
    path('propiedad/<int:pk>/', DetallePropiedadView.as_view(), name='propiedad_detallada'),
    path('autocompletar-direcciones/', autocompletar_direcciones, name='autocompletar_direcciones'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
