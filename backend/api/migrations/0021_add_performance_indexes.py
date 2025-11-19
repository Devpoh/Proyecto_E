# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_rename_productos_stock_idx_productos_stock_2e1108_idx_and_more'),
    ]

    operations = [
        # Índices para Producto
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['en_carrusel', 'activo', '-created_at'], name='producto_carousel_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['activo', 'categoria'], name='producto_active_cat_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['stock_total', 'stock_reservado', 'stock_vendido'], name='producto_stock_idx'),
        ),
        
        # Índices para CartItem
        migrations.AddIndex(
            model_name='cartitem',
            index=models.Index(fields=['cart', 'product'], name='cartitem_cart_prod_idx'),
        ),
        
        # Índices para Favorito
        migrations.AddIndex(
            model_name='favorito',
            index=models.Index(fields=['usuario', 'producto'], name='favorito_user_prod_idx'),
        ),
        migrations.AddIndex(
            model_name='favorito',
            index=models.Index(fields=['producto'], name='favorito_producto_idx'),
        ),
    ]
