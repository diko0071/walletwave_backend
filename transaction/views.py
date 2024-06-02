from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Transaction, TransactionCategory, RecurringTransaction
from rest_framework.response import Response
from .serializers import TransactionSerializer, RecurringTransactionSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Count, Q, Sum
from .filters import TransactionsFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.forms.models import model_to_dict
from django.db import transaction as db_transaction
from .services import ai_transaction_converter
import json
import calendar
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncWeek
import datetime
from datetime import timedelta
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule
from .tasks import create_transaction_and_update_next_charge_date
from datetime import datetime
from chat.prompts import ai_transaction_converter_prompt
from django.db.models.functions import TruncMonth, TruncDay

def clear_cache():
    cache.clear()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_transactions(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(Transaction, id=id, user=user)
    serializer = TransactionSerializer(transaction, many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    data = request.data.copy()
    data['user'] = request.user.pk
    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(Transaction, id=id, user=user)
    serializer = TransactionSerializer(transaction, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        clear_cache()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(Transaction, id=id, user=user)
    transaction.delete()
    clear_cache()
    return Response({'message': 'Transaction was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions_stat(request):
    user = request.user
    user_transactions = Transaction.objects.filter(user=user)

    now = timezone.now().date()
    current_month_start = now.replace(day=1)
    last_day_of_current_month = calendar.monthrange(now.year, now.month)[1]
    current_month_end = now.replace(day=last_day_of_current_month)

    user_recurring_transactions = RecurringTransaction.objects.filter(
        user=user,
        next_charge_date__range=[current_month_start, current_month_end]
    ).values('next_charge_date', 'amount', 'description')

    total_upcoming_transactions_sum = RecurringTransaction.objects.filter(
        user=user,
        next_charge_date__range=[current_month_start, current_month_end]
    ).aggregate(total_sum=Sum('amount'))['total_sum'] or 0

    transactions_by_category = user_transactions.filter(
        transaction_date__range=[current_month_start, current_month_end]
    ).values('category').annotate(total_sum=Sum('converted_amount')).order_by('-total_sum')

    total_monthly_sum = user_transactions.filter(
        transaction_date__range=[current_month_start, current_month_end]
    ).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0

    sum_transactions_by_month = user_transactions.annotate(month=TruncMonth('transaction_date')).values('month').annotate(month_sum=Sum('converted_amount')).order_by('month')
    
    monthly_transactions_details = user_transactions.filter(
        transaction_date__range=[current_month_start, current_month_end]
    ).values('transaction_date').annotate(total_sum=Sum('converted_amount')).order_by('transaction_date')

    top_category_current_month = transactions_by_category.first()
    
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)
    same_period_last_month_end = previous_month_end.replace(day=now.day)

    total_same_period_last_month_sum = user_transactions.filter(
        transaction_date__range=[previous_month_start, same_period_last_month_end]
    ).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0

    monthly_change_absolute = total_monthly_sum - total_same_period_last_month_sum
    monthly_change_percentage = ((total_monthly_sum - total_same_period_last_month_sum) / total_same_period_last_month_sum * 100) if total_same_period_last_month_sum != 0 else 0

    data = {
        'transactions_by_category': list(transactions_by_category),
        'total_monthly_sum': total_monthly_sum,
        'monthly_transactions_details': list(monthly_transactions_details),
        'transactions_by_month': list(sum_transactions_by_month),
        'top_category_current_month': top_category_current_month,
        'monthly_sum_comparison': {
            'current_month_sum': total_monthly_sum,
            'previous_month_sum': total_same_period_last_month_sum,
            'absolute_change': monthly_change_absolute,
            'percentage_change': monthly_change_percentage,
        },
        'upcoming_recurring_transactions': list(user_recurring_transactions),
        'total_upcoming_transactions_sum': total_upcoming_transactions_sum
    }

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ai_transactions(request):
    text_input = request.data.get('text')
    if not text_input:
        return Response({"error": "Text input is required"}, status=status.HTTP_400_BAD_REQUEST)

    system_message = ai_transaction_converter_prompt
    
    system_message = system_message + "Use currency by default (ONLY if user didn't specify currency)" + request.user.currency

    ai_response = ai_transaction_converter(text_input, system_message).content
    try:
        transactions_data = json.loads(ai_response)
        if isinstance(transactions_data, dict):

            transactions_data = [transactions_data]
        elif not isinstance(transactions_data, list):
            raise ValueError("AI response format is incorrect, expected a list of dictionaries")
    except (json.JSONDecodeError, ValueError) as e:
        return Response({"error": f"Failed to process AI response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    default_currency = request.user.currency
    response_data = []
    for transaction_data in transactions_data:
        transaction_instance = Transaction(
            user=request.user,
            amount=transaction_data['amount'],
            description=transaction_data['description'],
            category=transaction_data['category'],
            transaction_currency=transaction_data.get('transaction_currency', default_currency)
        )
        transaction_instance.save()
        transaction_dict = model_to_dict(transaction_instance)
        response_data.append({
            "id": transaction_dict['id'],
            "amount": transaction_dict['amount'],
            "description": transaction_dict['description'],
            "category": transaction_dict['category'],
            "transaction_currency": transaction_dict['transaction_currency']
        })
    clear_cache()
    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_recurring_transactions(request):
    user = request.user
    transactions = RecurringTransaction.objects.filter(user=user).order_by('-created_at')
    serializer = RecurringTransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recurring_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(RecurringTransaction, id=id, user=user)
    serializer = RecurringTransactionSerializer(transaction, many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_recurring_transaction(request):
    data = request.data.copy()
    data['user'] = request.user.pk
    serializer = RecurringTransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_recurring_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(RecurringTransaction, id=id, user=user)
    serializer = RecurringTransactionSerializer(transaction, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_recurring_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(RecurringTransaction, id=id, user=user)
    
    task_name_prefix = f"Create Transaction and Update Next Charge Date - transaction_id: {transaction.id}"
    PeriodicTask.objects.filter(name__startswith=task_name_prefix).delete()
    
    transaction.delete()
    return Response({'message': 'Recurring transaction was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)