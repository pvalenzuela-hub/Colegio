# Generated by Django 3.2.7 on 2024-05-03 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0005_alter_mensaje_idmensajerespondido'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mensaje',
            old_name='idmensajerespondido',
            new_name='mensajerespondidoid',
        ),
    ]
