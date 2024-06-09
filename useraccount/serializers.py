from rest_framework import serializers
from .models import User

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'currency', 'email', 'openai_key', 'telegram_key'
        )

