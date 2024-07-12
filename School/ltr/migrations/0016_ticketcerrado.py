# Generated by Django 3.2.7 on 2024-06-10 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0015_auto_20240528_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticketcerrado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('textocierre', models.CharField(max_length=200)),
                ('fechacierre', models.DateTimeField(auto_now=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ltr.ticket')),
            ],
            options={
                'db_table': 'TicketCerrados',
                'ordering': ['ticket'],
            },
        ),
    ]