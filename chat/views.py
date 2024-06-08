from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .models import ChatSession, ChatMessage
from transaction.models import Transaction
from transaction.serializers import TransactionSummarySerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .services import ai_reponse
from .prompts import personal_finance_assistant_prompt
from .services import validate_question
import json


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_all_chat_sessions(request):
    user = request.user
    chat_sessions = ChatSession.objects.filter(user=user)
    serializer = ChatSessionSerializer(chat_sessions, many=True)

    return Response(serializer.data)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_chat_session(request, pk):
    user = request.user
    chat_session = get_object_or_404(ChatSession, pk=pk, user=user)
    serializer = ChatSessionSerializer(chat_session)
    return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_chat_session(request):
    data = request.data.copy()
    data['user'] = request.user.pk
    serializer = ChatSessionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_chat_session(request, pk):
    user = request.user
    chat_session = get_object_or_404(ChatSession, pk=pk, user=user)
    data = request.data.copy()
    data['user'] = user.pk
    serializer = ChatSessionSerializer(chat_session, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_chat_session(request, pk):
    user = request.user
    chat_session = get_object_or_404(ChatSession, pk=pk, user=user)
    chat_session.delete()
    return Response({'message': 'Chat was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_answer(request, pk):
    user = request.user
    chat_session = get_object_or_404(ChatSession, pk=pk, user=user)

    transaction = Transaction.objects.filter(user=user)
    transaction_serializer = TransactionSummarySerializer(transaction, many=True)
    get_transaction_data = transaction_serializer.data
    api_key = request.user.openai_key

    if not api_key:
        return Response({"error": "No API key provided. Please provide a valid OpenAI API key."}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ChatMessageSerializer(data=request.data)
    if serializer.is_valid():
        chat_message = serializer.save(session=chat_session, system_message=chat_session.system_message)
        
        if validate_question(chat_message.human_message, api_key) == 1:
            system_message = personal_finance_assistant_prompt + json.dumps(get_transaction_data)
        else:
            system_message = personal_finance_assistant_prompt
        
        previous_messages = chat_session.previous_messages if chat_session.previous_messages else []
        
        aimessage_response = ai_reponse(
            human_message=chat_message.human_message,
            system_message=system_message,
            api_key=api_key,
            previous_messages=previous_messages,
        )
        
        content = aimessage_response.content
        
        chat_message.ai_message = content
        chat_message.json_response = repr(aimessage_response)
        chat_message.save()
        
        updated_previous_messages = previous_messages + [
            {"type": "human", "message": chat_message.human_message},
            {"type": "ai", "message": content}
        ]
        chat_session.previous_messages = updated_previous_messages
        chat_session.system_message = system_message
        chat_session.save()

        return Response({"response": content}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




