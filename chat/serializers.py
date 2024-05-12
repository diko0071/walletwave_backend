from rest_framework import serializers
from .models import ChatSession, ChatMessage, SystemMessage

class ChatSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatSession
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('session', 'human_message', 'ai_message', 'json_response', 'system_message')

class SystemMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMessage
        fields = '__all__'