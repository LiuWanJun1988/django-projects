# Generated by Django 3.2 on 2021-07-19 11:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
