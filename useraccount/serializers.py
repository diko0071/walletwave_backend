from rest_framework import serializers

from .models import User
from .tasks import email_welcome

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'currency', 'email'
        )