# Generated by Django 5.1.3 on 2024-11-18 19:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0005_remove_propiedades_imagen_galeria_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galeria',
            name='imagen',
            field=models.ImageField(upload_to='media/propiedades/'),
        ),
        migrations.AlterField(
            model_name='opiniones',
            name='calificacion',
            field=models.DecimalField(decimal_places=1, default=3, max_digits=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]