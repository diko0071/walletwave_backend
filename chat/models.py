from django.db import models
from useraccount.models import User
import requests
import os
import uuid
from .services import create_ai_title_for_session

class AIModel(models.TextChoices):
    GPT_4_TURBO = 'gpt-4-turbo'
    LLAMA_3 = 'llama-3'

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_name = models.CharField(max_length=255, default='New chat')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_model = models.CharField(max_length=255, choices=AIModel.choices,          
                                default=AIModel.GPT_4_TURBO)
    previous_messages = models.JSONField(blank=True, default=list)
    system_message = models.TextField(blank=True, default='')


    def save(self, *args, **kwargs):
        if self.session_name == "New chat" and self.previous_messages:
            self.session_name = create_ai_title_for_session(self.previous_messages)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ChatSession {self.session_name} for user {self.user.email}"
    
    
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    human_message = models.TextField()
    ai_message = models.TextField(blank=True, default='')
    json_response = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    system_message = models.TextField(blank=True, default='')

    def get_system_message(self):
        if self.system_message:
            return self.system_message
        return self.session.system_message
    
class SystemMessage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    prompt = models.TextField()

    def __str__(self):
        return self.name
