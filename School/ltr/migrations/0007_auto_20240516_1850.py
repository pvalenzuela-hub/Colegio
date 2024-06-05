# Generated by Django 3.2.7 on 2024-05-16 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0006_rename_idmensajerespondido_mensaje_mensajerespondidoid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nivel',
            options={'ordering': ['orden']},
        ),
        migrations.AddField(
            model_name='colegio',
            name='setting_name',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='ticket',
            name='numticket',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Ticketcorrelativo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('correlativo', models.IntegerField()),
                ('colegio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ltr.colegio')),
            ],
            options={
                'db_table': 'Ticketcorrelativo',
                'ordering': ['id'],
            },
        ),
    ]