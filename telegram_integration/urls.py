from django.urls import path
from .views import *

urlpatterns = [
    path('telegram_auth/', telegram_auth, name='telegram_auth'),
]