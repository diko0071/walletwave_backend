from celery import shared_task
from django.utils.timezone import now
from django.utils import timezone
import calendar
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from datetime import datetime
import os
import requests
from useraccount.models import User
from .views import send_message
from transaction.views import weekly_transactions_report, ai_weekly_report
from django.http import HttpRequest, HttpResponse
from transaction.models import TransactionReportType
from transaction.serializers import TransactionReportSerializer

@shared_task(name='telegram_integration.tasks.send_weekly_insights')
def send_weekly_insights(chat_id, user_id):
    request = HttpRequest()
    user = User.objects.get(id=user_id)
    request.user = user
    spend_report = weekly_transactions_report(request)
    insight_report = ai_weekly_report(request)

    spend_report = spend_report.data
    insight_report = insight_report.data
    insight_report = insight_report.content

    final_response = f'📆 Weekly Report\n\n💸 Weekly spend: {spend_report["total_spending"]}\n\n💡 Insights:\n\n {insight_report}'

    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': f'{final_response}'
    })

    now = timezone.now().date()  
    week_ago = now - timezone.timedelta(days=7)  
    report_data = {
        'user': user.id,
        'report': final_response,
        'type': TransactionReportType.WEEKLY,
        'period_start': week_ago,
        'period_end': now
    }
    report_serializer = TransactionReportSerializer(data=report_data)
    if report_serializer.is_valid():
        report_serializer.save()
    else:
        print(report_serializer.errors)

    return HttpResponse('Weekly report sent')