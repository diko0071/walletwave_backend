# Generated by Django 5.0.2 on 2024-06-10 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('useraccount', '0003_user_telegram_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='telegram_key',
        ),
    ]
