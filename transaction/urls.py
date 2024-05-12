from django.urls import path
from .views import *

urlpatterns = [
    path('transactions/', get_all_transactions, name='get_all_transactions'),
    path('transactions/<int:id>/', get_transaction, name='get_transaction'),
    path('transactions/create/', create_transaction, name='create_transaction'),
    path('transactions/<int:id>/update/', update_transaction, name='update_transaction'),
    path('transactions/<int:id>/delete/', delete_transaction, name='delete_transaction'),
    path('transactions/stats/', get_transactions_stat, name='get_transactions_stat'),
    path('transactions/create/ai/', create_ai_transactions, name='create_ai_transactions'),
    path('transactions/recurring/', get_all_recurring_transactions, name='get_all_recurring_transactions'),
    path('transactions/recurring/<int:id>/', get_recurring_transaction, name='get_recurring_transaction'),
    path('transactions/recurring/create/', create_recurring_transaction, name='create_recurring_transaction'),
    path('transactions/recurring/<int:id>/update/', update_recurring_transaction, name='update_recurring_transaction'),
    path('transactions/recurring/<int:id>/delete/', delete_recurring_transaction, name='delete_recurring_transaction'),
]

