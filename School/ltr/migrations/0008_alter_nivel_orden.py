# Generated by Django 3.2.7 on 2024-04-10 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0007_auto_20240410_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nivel',
            name='orden',
            field=models.IntegerField(),
        ),
    ]
