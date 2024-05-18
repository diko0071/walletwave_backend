from celery import shared_task
from django.utils.timezone import now
import calendar

@shared_task
def set_next_charge_date(recurring_transaction_id):
    from transaction.models import RecurringTransaction
    recurring_transaction = RecurringTransaction.objects.get(id=recurring_transaction_id)
    today = now().date()
    current_month_days = calendar.monthrange(today.year, today.month)[1]

    if recurring_transaction.charge_day > current_month_days:
        recurring_transaction.charge_day = current_month_days

    if today.day < recurring_transaction.charge_day:
        recurring_transaction.next_charge_date = today.replace(day=recurring_transaction.charge_day)
    else:
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        next_month_days = calendar.monthrange(next_year, next_month)[1]
        charge_day = min(recurring_transaction.charge_day, next_month_days)
        recurring_transaction.next_charge_date = today.replace(year=next_year, month=next_month, day=charge_day)

    recurring_transaction.save()