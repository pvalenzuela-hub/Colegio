# Generated by Django 3.2.7 on 2024-04-10 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0003_auto_20240406_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsignacionDirectorio',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'AsignacionDirectorio',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='AsignacionJefatura',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'AsignacionJefaturas',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='AsignacionResponsable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'AsignacionResponsables',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Ciclos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'Ciclos',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Personas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('telefono', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'Personas',
                'ordering': ['nombre'],
            },
        ),
        migrations.RemoveField(
            model_name='cargo',
            name='colegio',
        ),
        migrations.RemoveField(
            model_name='responsable',
            name='cargo',
        ),
        migrations.RemoveField(
            model_name='ticketalumno',
            name='curso',
        ),
        migrations.RemoveField(
            model_name='ticketalumno',
            name='nivel',
        ),
        migrations.RemoveField(
            model_name='ticketalumno',
            name='ticket',
        ),
        migrations.AddField(
            model_name='ticket',
            name='apellidoalumno',
            field=models.CharField(default='', max_length=80),
        ),
        migrations.AddField(
            model_name='ticket',
            name='curso',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.curso'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='nivel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.nivel'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='nombrealumno',
            field=models.CharField(default='', max_length=80),
        ),
        migrations.DeleteModel(
            name='Asignacion',
        ),
        migrations.DeleteModel(
            name='Cargo',
        ),
        migrations.DeleteModel(
            name='Responsable',
        ),
        migrations.DeleteModel(
            name='TicketAlumno',
        ),
        migrations.AddField(
            model_name='asignacionresponsable',
            name='ciclo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.ciclos'),
        ),
        migrations.AddField(
            model_name='asignacionresponsable',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ltr.personas'),
        ),
        migrations.AddField(
            model_name='asignacionresponsable',
            name='subarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.subarea'),
        ),
        migrations.AddField(
            model_name='asignacionjefatura',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ltr.personas'),
        ),
        migrations.AddField(
            model_name='asignacionjefatura',
            name='subarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.subarea'),
        ),
        migrations.AddField(
            model_name='asignaciondirectorio',
            name='ciclo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.ciclos'),
        ),
        migrations.AddField(
            model_name='asignaciondirectorio',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ltr.personas'),
        ),
        migrations.AddField(
            model_name='nivel',
            name='ciclo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.ciclos'),
        ),
    ]
