# Generated by Django 5.1.3 on 2024-11-23 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0007_alter_galeria_imagen_alter_opiniones_calificacion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propiedades',
            name='porcentaje_reserva',
        ),
    ]
