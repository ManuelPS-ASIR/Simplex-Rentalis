# Generated by Django 5.1.3 on 2024-11-23 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0008_remove_propiedades_porcentaje_reserva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propiedades',
            name='nombre',
            field=models.CharField(max_length=100),
        ),
    ]
