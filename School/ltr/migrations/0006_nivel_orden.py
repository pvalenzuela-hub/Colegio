# Generated by Django 3.2.7 on 2024-04-10 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ltr', '0005_auto_20240410_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='nivel',
            name='orden',
            field=models.CharField(default='1', max_length=1),
        ),
    ]
