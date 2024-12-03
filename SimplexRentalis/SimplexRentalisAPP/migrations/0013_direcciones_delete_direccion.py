# Generated by Django 5.1.3 on 2024-12-03 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0012_direccion_codigo_postal_direccion_numero_casa_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direcciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calle', models.CharField(max_length=255)),
                ('numero_casa', models.CharField(max_length=20)),
                ('numero_puerta', models.CharField(blank=True, max_length=20, null=True)),
                ('codigo_postal', models.CharField(max_length=20)),
                ('ciudad', models.CharField(max_length=100)),
                ('co_autonoma', models.CharField(max_length=100)),
                ('provincia', models.CharField(max_length=100)),
                ('pais', models.CharField(max_length=100)),
                ('latitud', models.FloatField(blank=True, null=True)),
                ('longitud', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Direccion',
        ),
    ]
