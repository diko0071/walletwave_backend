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
]

