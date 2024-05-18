from celery import shared_task
from django.utils.timezone import now
import calendar
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from datetime import datetime

@shared_task
def create_transaction_and_update_next_charge_date(recurring_transaction_id):
    from .models import RecurringTransaction, Transaction
    recurring_transaction = RecurringTransaction.objects.get(id=recurring_transaction_id)
    today = now().date()

    if recurring_transaction.next_charge_date == today:
        transaction = Transaction.objects.create(
            user=recurring_transaction.user,
            amount=recurring_transaction.amount,
            description=recurring_transaction.description,
            category=recurring_transaction.category,
            transaction_currency=recurring_transaction.currency,
            transaction_type='Recurring',
            transaction_date=today
        )
        print(f'Транзакция создана: {transaction}')

        current_month_days = calendar.monthrange(today.year, today.month)[1]
        if recurring_transaction.charge_day > current_month_days:
            recurring_transaction.charge_day = current_month_days

        if today.day < recurring_transaction.charge_day:
            next_charge_date = today.replace(day=recurring_transaction.charge_day)
        else:
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year if today.month < 12 else today.year + 1
            next_month_days = calendar.monthrange(next_year, next_month)[1]
            charge_day = min(recurring_transaction.charge_day, next_month_days)
            next_charge_date = today.replace(year=next_year, month=next_month, day=charge_day)

        recurring_transaction.next_charge_date = next_charge_date
        recurring_transaction.save()