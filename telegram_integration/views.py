import hashlib
import hmac
import time
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from .models import TelegramUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from backend.settings import TELEGRAM_BOT_TOKEN

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_auth(request):
    bot_token = TELEGRAM_BOT_TOKEN
    data = request.GET

    telegram_id = data.get('id')
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id, 
        defaults={
            'username': username, 
            'first_name': first_name, 
            'last_name': last_name,
            'user': request.user
        }
    )

    return JsonResponse({'status': 'success', 'message': 'Authentication successful'}, status=200)