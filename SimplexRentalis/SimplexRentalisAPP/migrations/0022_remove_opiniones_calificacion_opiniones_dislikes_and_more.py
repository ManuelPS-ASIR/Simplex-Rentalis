# Generated by Django 4.2.16 on 2024-12-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0021_identidadreserva_identidadusuario_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opiniones',
            name='calificacion',
        ),
        migrations.AddField(
            model_name='opiniones',
            name='dislikes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='opiniones',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]