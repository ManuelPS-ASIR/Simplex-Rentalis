from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Importar vistas de autenticación

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),  # Usamos la vista personalizada de login
    path('logout/', views.logout_view, name='logout'),  # Usamos nuestra vista personalizada de logout
    path('registro/', views.register, name='register'),
    #Modificación en cuenta
    path('settings/', views.account_settings, name='account_settings'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('delete_account/', views.delete_account_view, name='delete_account'),

    # Otras rutas
    path('settings/', views.account_settings, name='settings'),
    # Rutas para la aplicación
    path("", views.index, name="index"),
    path('propiedades/', views.propiedades, name='propiedades'),
    path('propiedades/mis_propiedades/', views.propiedades_usuario, name='propiedades_usuario'),
]