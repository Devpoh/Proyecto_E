# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_stockreservation_user_agent'),
    ]

    operations = [
        # Agregar índices simples
        migrations.AlterField(
            model_name='producto',
            name='en_carrusel',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='producto',
            name='activo',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='producto',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        
        # Agregar índices compuestos
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['en_carrusel', 'activo'], name='api_producto_en_carrusel_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['categoria', 'activo'], name='api_producto_categoria_activo_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['-created_at'], name='api_producto_created_at_desc_idx'),
        ),
    ]
