from rest_framework import serializers
from .models import ChatSession, ChatMessage
from useraccount.models import User

class ChatSessionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = ChatSession
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = ('session', 'human_message', 'ai_message', 'json_response', 'system_message')