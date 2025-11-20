# Generated migration for adding visibility fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_add_imagen_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="en_carousel_card",
            field=models.BooleanField(default=True, help_text="Mostrar en CarouselCard (tarjetas inferiores)"),
        ),
        migrations.AddField(
            model_name="producto",
            name="en_all_products",
            field=models.BooleanField(default=True, help_text="Mostrar en AllProducts (catálogo completo)"),
        ),
    ]
