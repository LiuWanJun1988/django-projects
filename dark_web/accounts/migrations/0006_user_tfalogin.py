# Generated by Django 2.1.5 on 2019-03-06 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20190202_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tfalogin',
            field=models.BooleanField(default=False),
        ),
    ]