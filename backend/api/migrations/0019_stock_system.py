# Generated migration for stock reservation system

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_producto_categoria'),
    ]

    operations = [
        # ✅ Agregar campos de stock al modelo Producto
        migrations.AddField(
            model_name='producto',
            name='stock_total',
            field=models.IntegerField(default=0, help_text='Stock físico total del almacén'),
        ),
        migrations.AddField(
            model_name='producto',
            name='stock_reservado',
            field=models.IntegerField(default=0, help_text='Stock apartado por clientes en Checkout'),
        ),
        migrations.AddField(
            model_name='producto',
            name='stock_vendido',
            field=models.IntegerField(default=0, help_text='Stock ya vendido/completado'),
        ),
        
        # ✅ Agregar índices para optimización
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['stock'], name='productos_stock_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['stock_reservado'], name='productos_stock_reservado_idx'),
        ),
        
        # ✅ Crear modelo StockReservation
        migrations.CreateModel(
            name='StockReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(help_text='Cantidad reservada')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pendiente'),
                        ('confirmed', 'Confirmado'),
                        ('cancelled', 'Cancelado'),
                        ('expired', 'Expirado'),
                    ],
                    db_index=True,
                    default='pending',
                    help_text='Estado de la reserva',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación de la reserva')),
                ('expires_at', models.DateTimeField(help_text='Fecha de expiración (TTL: 15 minutos por defecto)')),
                ('confirmed_at', models.DateTimeField(blank=True, help_text='Fecha de confirmación del pago', null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, help_text='Fecha de cancelación', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP del cliente', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User-Agent del navegador')),
                ('producto', models.ForeignKey(help_text='Producto reservado', on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='api.producto')),
                ('usuario', models.ForeignKey(help_text='Usuario que realizó la reserva', on_delete=django.db.models.deletion.CASCADE, related_name='stock_reservations', to='auth.user')),
            ],
            options={
                'verbose_name': 'Reserva de Stock',
                'verbose_name_plural': 'Reservas de Stock',
                'db_table': 'stock_reservations',
                'ordering': ['-created_at'],
            },
        ),
        
        # ✅ Agregar índices a StockReservation
        migrations.AddIndex(
            model_name='stockreservation',
            index=models.Index(fields=['usuario', 'status'], name='stock_reservations_usuario_status_idx'),
        ),
        migrations.AddIndex(
            model_name='stockreservation',
            index=models.Index(fields=['producto', 'status'], name='stock_reservations_producto_status_idx'),
        ),
        migrations.AddIndex(
            model_name='stockreservation',
            index=models.Index(fields=['status', 'expires_at'], name='stock_reservations_status_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='stockreservation',
            index=models.Index(fields=['expires_at'], name='stock_reservations_expires_idx'),
        ),
    ]
