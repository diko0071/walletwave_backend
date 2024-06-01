from celery import shared_task
from django.utils.timezone import now
from django.utils import timezone
import calendar
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from datetime import datetime
import os
import requests


@shared_task(name='transaction.tasks.create_transaction_and_update_next_charge_date')
def create_transaction_and_update_next_charge_date(recurring_transaction_id):
    from .models import RecurringTransaction, Transaction
    recurring_transaction = RecurringTransaction.objects.get(id=recurring_transaction_id)
    today = timezone.now().date()

    if recurring_transaction.next_charge_date == today:
        print('Transaction today!')
        transaction = Transaction.objects.create(
            user_id=recurring_transaction.user_id,
            amount=recurring_transaction.amount,
            description=recurring_transaction.description,
            category=recurring_transaction.category,
            transaction_currency=recurring_transaction.currency,
            transaction_type='Recurring',
            transaction_date=today
        )
            
        current_month_days = calendar.monthrange(today.year, today.month)[1]
        if recurring_transaction.charge_day > current_month_days:
            recurring_transaction.charge_day = current_month_days

        if today.day < recurring_transaction.charge_day:
            next_charge_date = today.replace(day=recurring_transaction.charge_day)
            print(f'This new next charge date: {next_charge_date}')
            recurring_transaction.next_charge_date = next_charge_date
            recurring_transaction.save(update_fields=['next_charge_date'])
        else:
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year if today.month < 12 else today.year + 1
            next_month_days = calendar.monthrange(next_year, next_month)[1]
            charge_day = min(recurring_transaction.charge_day, next_month_days)
            next_charge_date = today.replace(year=next_year, month=next_month, day=charge_day)
            print(f'This new next charge date: {next_charge_date}')
            recurring_transaction.next_charge_date = next_charge_date
            recurring_transaction.save(update_fields=['next_charge_date'])


@shared_task(name='transaction.tasks.email_before_reccuring_transaction')
def email_before_reccuring_transaction(user_id, transaction_id):
    print(f'Email before recurring transaction for user_id: {user_id}')
    from useraccount.models import User
    from .models import RecurringTransaction

    user = User.objects.get(id=user_id)
    email, name = user.email, user.name

    recurring_transactions = RecurringTransaction.objects.filter(user_id=user_id, id=transaction_id)

    for transaction in recurring_transactions:
        description, amount, currency = transaction.description, transaction.amount, transaction.currency
    
    url = "https://app.loops.so/api/v1/transactional"

    if name is None:
        name = ""

    payload = {
        "transactionalId": "clwvbrtz901k0lb4dxysn046m",
        "email": email,
        "dataVariables": {
            "name": name,
            "description": description,
            "amount": int(amount),
            "currency": currency,
        }
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('LOOPS_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()