# Generated by Django 5.0.2 on 2024-05-31 03:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_chatsession_session_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SystemMessage',
        ),
    ]
