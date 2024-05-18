from rest_framework import serializers
from .models import Transaction, RecurringTransaction
from useraccount.models import User
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
import json 
import uuid
from .tasks import create_transaction_and_update_next_charge_date

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'

class RecurringTransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = RecurringTransaction
        fields = '__all__'

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        self.create_or_update_periodic_task(instance)
        return instance

    def create_or_update_periodic_task(self, instance):
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_month=str(instance.charge_day),
            month_of_year='*',
            day_of_week='*',
        )

        task_name = f"Create Transaction and Update Next Charge Date - transaction_id: {instance.id}, task_id: {uuid.uuid4()}"
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name=task_name,
            defaults={
                'task': 'transaction.tasks.create_transaction_and_update_next_charge_date',
                'args': json.dumps([instance.id]),
            }
        )

        if not created:
            task.crontab = schedule
            task.args = json.dumps([instance.id])
            task.task = 'transaction.tasks.create_transaction_and_update_next_charge_date'
            task.save()

        today = timezone.now().day
        if today == instance.charge_day:
            create_transaction_and_update_next_charge_date.apply_async(args=[instance.id])