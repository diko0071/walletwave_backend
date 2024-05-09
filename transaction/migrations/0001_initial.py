# Generated by Django 5.0.4 on 2024-05-06 21:52

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("description", models.CharField(max_length=300)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Travel", "Travel"),
                            ("Food & Drinks", "Food"),
                            ("Entertainment", "Entertainment"),
                            ("Utilities & Bills", "Utilities"),
                            ("Health & Wellness", "Health"),
                            ("Shopping", "Shopping"),
                            ("Education", "Education"),
                            ("Gifts", "Gift"),
                            ("Rent", "Rent"),
                            ("Other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "transaction_currency",
                    models.CharField(
                        choices=[
                            ("USD", "Usd"),
                            ("EUR", "Eur"),
                            ("RUB", "Rub"),
                            ("AED", "Aed"),
                            ("GBP", "Gbp"),
                            ("AUD", "Aud"),
                            ("KZT", "Kzt"),
                        ],
                        default="USD",
                        max_length=20,
                    ),
                ),
                (
                    "converted_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "converted_currency",
                    models.CharField(blank=True, max_length=3, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
