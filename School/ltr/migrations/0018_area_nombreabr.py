# Generated by Django 3.2.7 on 2024-06-13 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0017_ticketcerrado_persona'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='nombreabr',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]