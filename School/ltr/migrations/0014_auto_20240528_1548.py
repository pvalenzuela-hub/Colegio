# Generated by Django 3.2.7 on 2024-05-28 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0013_accesocolegio'),
    ]

    operations = [
        migrations.AddField(
            model_name='colegio',
            name='logofirma',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='colegio',
            name='logoprincipal',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='accesocolegio',
            name='colegioactual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='actual_acceso_colegio', to='ltr.colegio', verbose_name='Colegio Actual'),
        ),
        migrations.AlterField(
            model_name='accesocolegio',
            name='colegiodefault',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='default_acceso_colegio', to='ltr.colegio', verbose_name='Colegio Default'),
        ),
    ]
