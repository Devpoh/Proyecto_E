# Generated migration for Favorito model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0014_cartauditlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de agregación a favoritos')),
                ('producto', models.ForeignKey(help_text='Producto marcado como favorito', on_delete=django.db.models.deletion.CASCADE, related_name='favoritos', to='api.producto')),
                ('usuario', models.ForeignKey(help_text='Usuario que marcó como favorito', on_delete=django.db.models.deletion.CASCADE, related_name='favoritos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favorito',
                'verbose_name_plural': 'Favoritos',
                'db_table': 'favoritos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='favorito',
            constraint=models.UniqueConstraint(fields=('usuario', 'producto'), name='unique_usuario_producto'),
        ),
    ]
