from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Importar vistas de autenticación

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),  # Usamos la vista personalizada de login
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Cierre de sesión estándar

    # Otras rutas
    path('registro/', views.register, name='register'),
    path('account/settings/', views.account_settings, name='account_settings'),

    # Rutas para la aplicación
    path("", views.index, name="index"),
    path('propiedades/', views.propiedades, name='propiedades'),
    path('propiedades/mis_propiedades/', views.propiedades_usuario, name='propiedades_usuario'),
]
