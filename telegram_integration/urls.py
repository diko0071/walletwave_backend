from django.urls import path
from .views import telegram_bot, setwebhook, delete_webhook

urlpatterns = [
  path('getpost/', telegram_bot, name='telegram_bot'),
  path('setwebhook/', setwebhook, name='setwebhook'),
  path('deletewebhook/', delete_webhook, name='deletewebhook'),
]