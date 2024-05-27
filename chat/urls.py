from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', get_all_chat_sessions, name='get_all_chat_sessions'),
    path('chat/<int:pk>/', get_chat_session, name='get_chat_session'),
    path('chat/create/', create_chat_session, name='create_chat_session'),
    path('chat/<int:pk>/answer/', get_answer, name='get_answer'),
    path('chat/<int:pk>/update/', update_chat_session, name='update_chat_session'),
    path('chat/<int:pk>/delete/', delete_chat_session, name='delete_chat_session'),
]

