# Generated by Django 5.0.2 on 2024-05-15 23:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0005_transaction_transaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]