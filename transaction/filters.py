from django_filters import rest_framework as filters
from django_filters import DateFromToRangeFilter, NumberFilter

from .models import Transaction

class TransactionsFilter(filters.FilterSet):
    keyword = filters.CharFilter(field_name='description', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    created_at_month = NumberFilter(field_name='created_at', lookup_expr='month', label='Created at month')
    created_at_year = NumberFilter(field_name='created_at', lookup_expr='year', label='Created at year')

    class Meta:
        model = Transaction
        fields = ('category', 'description', 'created_at', 'keyword')