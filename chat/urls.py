from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', get_all_chat_sessions, name='get_all_chat_sessions'),
    path('chat/<int:pk>/', get_chat_session, name='get_chat_session'),
    path('chat/create/', create_chat_session, name='create_chat_session'),
    path('chat/<int:pk>/answer/', get_answer, name='get_answer'),
]

