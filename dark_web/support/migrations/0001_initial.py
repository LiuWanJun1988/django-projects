# Generated by Django 2.1.5 on 2019-01-09 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('ended', models.DateTimeField(blank=True, null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='name', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('sent', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='support.Chat')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_message_name', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]