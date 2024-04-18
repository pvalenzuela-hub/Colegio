# Generated by Django 3.2.7 on 2024-04-06 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0002_rename_colegio_tipocontacto_cole'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipocontacto',
            name='cole',
        ),
        migrations.AddField(
            model_name='tipocontacto',
            name='colegio',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.colegio'),
        ),
    ]
