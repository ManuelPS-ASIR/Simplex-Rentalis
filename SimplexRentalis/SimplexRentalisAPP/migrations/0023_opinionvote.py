# Generated by Django 4.2.16 on 2024-12-14 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SimplexRentalisAPP', '0022_remove_opiniones_calificacion_opiniones_dislikes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpinionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=7)),
                ('opinion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SimplexRentalisAPP.opiniones')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('opinion', 'user')},
            },
        ),
    ]
