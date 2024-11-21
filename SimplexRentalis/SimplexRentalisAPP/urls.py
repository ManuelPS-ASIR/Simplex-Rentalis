from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Importar vistas de autenticación
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),  # Usamos la vista personalizada de login
    path('logout/', views.logout_view, name='logout'),  # Usamos nuestra vista personalizada de logout
    path('registro/', views.register, name='register'),
    
    # Modificación en cuenta
    path('settings/', views.account_settings, name='settings'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('delete_account/', views.delete_account, name='delete_account'),

    # Rutas para la aplicación
    path("", views.index, name="index"),
    path('propiedades/', views.propiedades, name='propiedades'),
    
    # Ruta correcta para "Mis Propiedades"
    path('mis_propiedades/', views.propiedades_usuario, name='propiedades_usuario'),
    
    # Ruta para agregar propiedad
    path('propiedades/agregar/', views.agregar_propiedad, name='agregar_propiedad'),
    path('agregar/', views.agregar_propiedad, name='agregar_propiedad'),
    
    # Ruta para ver detalle de la propiedad
    path('propiedad/<int:propiedad_id>/', views.propiededad_detallada, name='propiedad_detallada'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
