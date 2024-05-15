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
from chat.serializers import SystemMessageSerializer
from chat.models import SystemMessage
from django.forms.models import model_to_dict
from django.db import transaction as db_transaction
from .services import ai_transaction_converter
import json
import calendar
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncWeek
import datetime
from datetime import timedelta

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
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction(request, id):
    user = request.user
    transaction = get_object_or_404(Transaction, id=id, user=user)
    transaction.delete()
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
    
    previous_month_date = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_date.replace(day=1)
    last_day_of_previous_month = calendar.monthrange(previous_month_date.year, previous_month_date.month)[1]
    previous_month_end = previous_month_date.replace(day=last_day_of_previous_month)
    
    current_week_start = now - timedelta(days=now.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = current_week_end - timedelta(days=7)

    today_start = now
    today_end = now
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = yesterday_start

    today_sum = user_transactions.filter(transaction_date__range=[today_start, today_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    yesterday_sum = user_transactions.filter(transaction_date__range=[yesterday_start, yesterday_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    daily_change = round(((today_sum - yesterday_sum) / yesterday_sum * 100) if yesterday_sum != 0 else 0, 2)
    daily_change_absolute = round(today_sum - yesterday_sum, 2)

    monthly_sum = user_transactions.filter(transaction_date__range=[current_month_start, current_month_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    previous_month_sum = user_transactions.filter(transaction_date__range=[previous_month_start, previous_month_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    monthly_change = round(((monthly_sum - previous_month_sum) / previous_month_sum * 100) if previous_month_sum != 0 else 0, 2)
    
    weekly_sum = user_transactions.filter(transaction_date__range=[current_week_start, current_week_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    previous_week_sum = user_transactions.filter(transaction_date__range=[previous_week_start, previous_week_end]).aggregate(total_sum=Sum('converted_amount'))['total_sum'] or 0
    weekly_change = round(((weekly_sum - previous_week_sum) / previous_week_sum * 100) if previous_week_sum != 0 else 0, 2)
    
    current_month_transactions_count = user_transactions.filter(transaction_date__range=[current_month_start, current_month_end]).count()
    previous_month_transactions_count = user_transactions.filter(transaction_date__range=[previous_month_start, previous_month_end]).count()
    transactions_count_change = round(((current_month_transactions_count - previous_month_transactions_count) / previous_month_transactions_count * 100) if previous_month_transactions_count != 0 else 0, 2)
    
    top_category_current_month = user_transactions.filter(transaction_date__range=[current_month_start, current_month_end]).values('category').annotate(total=Count('id')).order_by('-total').first()
    top_category_previous_month = user_transactions.filter(transaction_date__range=[previous_month_start, previous_month_end]).values('category').annotate(total=Count('id')).order_by('-total').first()


    data = {
        'monthly_sum': monthly_sum,
        'monthly_change': monthly_change,
        'weekly_sum': weekly_sum,
        'weekly_change': weekly_change,
        'transactions_count': current_month_transactions_count,
        'transactions_count_change': transactions_count_change,
        'top_category_current_month': top_category_current_month,
        'top_category_previous_month': top_category_previous_month,
        'today_sum': today_sum,
        'yesterday_sum': yesterday_sum,
        'daily_change': daily_change,
        'daily_change_absolute': daily_change_absolute,
    }

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ai_transactions(request):
    text_input = request.data.get('text')
    if not text_input:
        return Response({"error": "Text input is required"}, status=status.HTTP_400_BAD_REQUEST)

    system_message = ""
    try:
        system_message = SystemMessage.objects.get(name="ai_transaction_converter").prompt
        system_message = system_message + "Use currency by default (ONLY if user didn't specify currency)" + request.user.currency
    except SystemMessage.DoesNotExist:
        pass

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
    transaction.delete()
    return Response({'message': 'Recurring transaction was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)