from django.db import models
from useraccount.models import User
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.apps import apps
import os
import datetime
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils.timezone import now
import calendar
from .tasks import create_transaction_and_update_next_charge_date

class TransactionCategory(models.TextChoices):
    TRAVEL = "Travel"
    FOOD = "Food & Drinks"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities & Bills"
    HEALTH = "Health & Wellness"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    GIFT = "Gifts"
    RENT = "Rent"
    SUBSCRIPTION = "Subscription"
    OTHER = "Other"

class TransactionCurrency(models.TextChoices):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    AED = "AED"
    GBP = "GBP"
    AUD = "AUD"
    KZT = "KZT"

class TransactionType(models.TextChoices):
    REGULAR = "Regular"
    RECURRING = "Recurring"

class TransactionFrequency(models.TextChoices):
    MONTHLY = "Monthly"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300)
    category = models.CharField(max_length=20, choices=TransactionCategory.choices)
    transaction_currency = models.CharField(max_length=20, choices=TransactionCurrency.choices, default=TransactionCurrency.USD)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    converted_currency = models.CharField(max_length=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, default=TransactionType.REGULAR)
    transaction_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.description} - {self.amount} {self.transaction_currency}"
    
    @staticmethod
    def currency_converter(amount, from_currency, to_currency):
        base_url = os.getenv('EXCHANGE_RATE_API_URL')
        url = f"{base_url}{from_currency}"

        response = requests.get(url)
        data = response.json()
        print("data", data)

        if data['result'] != 'success':
            return None
        
        conversion_rates = data.get('conversion_rates', {})
        from_rate = Decimal(conversion_rates.get(from_currency, 0))
        to_rate = Decimal(conversion_rates.get(to_currency, 0))
        print("from_rate", from_rate, "to_rate", to_rate)
        if from_rate == 0 or to_rate == 0:
            return None
        
        conversion_factor = to_rate / from_rate
        print("conversion_factor", conversion_factor)
        return Decimal(amount) * conversion_factor
    
    def save(self, *args, **kwargs):
        user_account = apps.get_model('useraccount', 'User')
        user_account_instance = user_account.objects.filter(id=self.user.id).first()

        if user_account_instance:
            user_currency = user_account_instance.currency
            if self.transaction_currency != user_currency:
                try:
                    converted_amount = self.currency_converter(self.amount,         
                    self.transaction_currency, user_currency)
                    if converted_amount is not None:
                        self.converted_amount = converted_amount.quantize(Decimal('0.01'))
                        self.converted_currency = user_currency
                except requests.exceptions.RequestException as e:
                    print(f"Error: {e}")
            else:
                self.converted_amount = self.amount
                self.converted_currency = self.transaction_currency

        super(Transaction, self).save(*args, **kwargs)

class RecurringTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300)
    category = models.CharField(max_length=20, choices=TransactionCategory.choices)
    charge_day = models.IntegerField()
    frequency = models.CharField(max_length=20, choices=TransactionFrequency.choices, default=TransactionFrequency.MONTHLY)
    currency = models.CharField(max_length=20, choices=TransactionCurrency.choices, default=TransactionCurrency.USD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_charge_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        today = now().date()
        current_month_days = calendar.monthrange(today.year, today.month)[1]

        if not self.next_charge_date:
            print('next_charge_date is None')
            if self.charge_day > current_month_days:
                self.charge_day = current_month_days

            if today.day < self.charge_day:
                self.next_charge_date = today.replace(day=self.charge_day)

            elif today.day == self.charge_day:
                self.next_charge_date = today
            else:
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                next_month_days = calendar.monthrange(next_year, next_month)[1]
                charge_day = min(self.charge_day, next_month_days)
                self.next_charge_date = today.replace(year=next_year, month=next_month, day=charge_day)

        else: 
            if today.day < self.charge_day:
                self.next_charge_date = today.replace(day=self.charge_day)
            else:
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                next_month_days = calendar.monthrange(next_year, next_month)[1]
                charge_day = min(self.charge_day, next_month_days)
                self.next_charge_date = today.replace(year=next_year, month=next_month, day=charge_day)

        super(RecurringTransaction, self).save(*args, **kwargs)

        def __str__(self):
            return f"{self.description} - {self.amount} {self.currency} - {self.frequency} - Day {self.charge_day} of each month"
        

class TransactionReportType(models.TextChoices):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class TrasactionReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=40, choices=TransactionReportType.choices, default=TransactionReportType.WEEKLY)
    period_start = models.DateField()
    period_end = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.period_start} - {self.period_end}"