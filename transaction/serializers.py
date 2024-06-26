from rest_framework import serializers
from .models import Transaction, RecurringTransaction, TrasactionReport
from useraccount.models import User
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
import json 
import uuid
import calendar
from .tasks import create_transaction_and_update_next_charge_date

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [ 'transaction_date', 'category', 'description', 'transaction_type', 'converted_amount', 'converted_currency']


class TransactionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrasactionReport
        fields = '__all__'


class RecurringTransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = RecurringTransaction
        fields = '__all__'

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        self.create_or_update_periodic_task(instance)
        self.create_or_update_email_notification_task(instance)
        return instance
    
    def delete(self, instance):
        PeriodicTask.objects.filter(name__contains=f"transaction_id: {instance.id}").delete()
        PeriodicTask.objects.filter(name__contains=f"Email Notification - transaction_id: {instance.id}").delete()
        super().delete(instance)

    def create_or_update_periodic_task(self, instance):
        existing_tasks = PeriodicTask.objects.filter(name__contains=f"transaction_id: {instance.id}")
        today = timezone.now().day

        if existing_tasks.exists():
            existing_tasks.delete()
            self.create_new_periodic_task(instance)
        
        else:
            print('no existing_task')
            self.create_new_periodic_task(instance)

        if today == instance.charge_day:
            print('today == charge_day')
            create_transaction_and_update_next_charge_date.apply_async(args=[instance.id])

    def create_new_periodic_task(self, instance):
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_month=str(instance.charge_day),
            month_of_year='*',
            day_of_week='*',
        )
        task_name = f"Create Transaction and Update Next Charge Date - transaction_id: {instance.id}, task_id: {uuid.uuid4()}"
        task = 'transaction.tasks.create_transaction_and_update_next_charge_date'
        PeriodicTask.objects.create(
            crontab=schedule,
            name=task_name,
            task=task,
            args=json.dumps([instance.id]),
        )


    def create_or_update_email_notification_task(self, instance):
        existing_tasks = PeriodicTask.objects.filter(name__contains=f"Email Notification - transaction_id: {instance.id}")

        if existing_tasks.exists():
            existing_tasks.delete()
            
        self.create_email_notification_task(instance)

    
    def create_email_notification_task(self, instance):

        current_month = timezone.now().month
        current_year = timezone.now().year

        if current_month == 1:
            previous_month = 12
            previous_year = current_year - 1
        else:
            previous_month = current_month - 1
            previous_year = current_year
       
        _, last_day = calendar.monthrange(previous_year, previous_month)

        if instance.charge_day == 1:
            day_of_month = str(last_day - 1)
        elif instance.charge_day == 2:
            day_of_month = str(last_day)
        else:
            day_of_month = str(instance.charge_day - 2)


        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_month=day_of_month,
            month_of_year='*',
            day_of_week='*',
        )

        task_name = f"Email Notification - transaction_id: {instance.id}, task_id: {uuid.uuid4()}"
        task = 'transaction.tasks.email_before_reccuring_transaction'
        PeriodicTask.objects.create(
            crontab=schedule,
            name=task_name,
            task=task,
            args=json.dumps([str(instance.user_id), instance.id]), 
        )
