# Generated by Django 3.2.7 on 2024-05-23 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0009_auto_20240523_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='personacierre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.personas'),
        ),
    ]
