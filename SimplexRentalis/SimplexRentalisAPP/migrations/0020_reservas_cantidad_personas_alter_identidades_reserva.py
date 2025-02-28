# Generated by Django 4.2.16 on 2024-12-11 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0019_identidades_usuario_user_identidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservas',
            name='cantidad_personas',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='identidades',
            name='reserva',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='identidades_reserva', to='SimplexRentalisAPP.reservas'),
            preserve_default=False,
        ),
    ]
