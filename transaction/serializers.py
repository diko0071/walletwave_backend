from rest_framework import serializers
from .models import Transaction, RecurringTransaction
from useraccount.models import User

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