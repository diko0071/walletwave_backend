from django.contrib import admin
from .models import ChatSession, ChatMessage, SystemMessage

admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(SystemMessage)