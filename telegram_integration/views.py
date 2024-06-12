import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from useraccount.models import User
from transaction.views import create_ai_transactions
from django.forms.models import model_to_dict
from transaction.models import Transaction
from transaction.services import ai_transaction_converter
from rest_framework.response import Response
from chat.prompts import ai_transaction_converter_prompt
from rest_framework import status
from dotenv import load_dotenv
import os

load_dotenv()

def create_telegram_transaction(request):
    text_input = request.data.get('text')
    if not text_input:
        return Response({"error": "Text input is required"}, status=status.HTTP_400_BAD_REQUEST)

    system_message = ai_transaction_converter_prompt
    
    system_message = system_message + "Use currency by default (ONLY if user didn't specify currency)" + request.user.currency

    api_key = request.user.openai_key

    if not api_key:
        return Response({"error": "No API key provided. Please provide a valid OpenAI API key."}, status=status.HTTP_400_BAD_REQUEST)

    ai_response = ai_transaction_converter(text_input, system_message, api_key).content
    try:
        transactions_data = json.loads(ai_response)
        if isinstance(transactions_data, dict):

            transactions_data = [transactions_data]
        elif not isinstance(transactions_data, list):
            raise ValueError("AI response format is incorrect, expected a list of dictionaries")
    except (json.JSONDecodeError, ValueError) as e:
        return Response({"error": f"Failed to process AI response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    default_currency = request.user.currency
    response_data = []
    for transaction_data in transactions_data:
        transaction_instance = Transaction(
            user=request.user,
            amount=transaction_data['amount'],
            description=transaction_data['description'],
            category=transaction_data['category'],
            transaction_currency=transaction_data.get('transaction_currency', default_currency)
        )
        transaction_instance.save()
        transaction_dict = model_to_dict(transaction_instance)
        response_data.append({
            "id": transaction_dict['id'],
            "amount": transaction_dict['amount'],
            "description": transaction_dict['description'],
            "category": transaction_dict['category'],
            "transaction_currency": transaction_dict['transaction_currency']
        })
    return Response(response_data, status=status.HTTP_201_CREATED)


def setwebhook(request):
  response = requests.post(os.getenv("TELEGRAM_BOT_API_URL") + "setWebhook?url=" + os.getenv("TELEGRAM_APP_API_URL")).json()
  print(response)
  return HttpResponse(f"{response}")

@csrf_exempt
def telegram_bot(request):
  if request.method == 'POST':
    update = json.loads(request.body.decode('utf-8'))
    handle_update(update, request)
    return HttpResponse('ok')
  else:
    return HttpResponseBadRequest('Bad Request')

def handle_update(update, request):
  chat_id = update['message']['chat']['id']
  
  try:
    user = User.objects.get(telegram_user_id=chat_id)
  
  except User.DoesNotExist:
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': 'You are not registered. Please sign up on our platform: https://walletwave.app'
    })
    
    return HttpResponse('User not registered')

  text = update['message']['text']

  if text == '/start':
    response_text = 'Welcome to WalletWave! Please send me your transactions in any format. I will create a transaction and add them to your transaction list!'

    send_message("sendMessage", {
    'chat_id': chat_id,
    'text': f'{response_text}'
  })
    return HttpResponse('Starter message sent')

  request.data = {'text': text}
  request.user = user

  response = create_telegram_transaction(request)

  transaction_data = response.data

  if response.status_code == status.HTTP_400_BAD_REQUEST and response.data.get('error') == "No API key provided. Please provide a valid OpenAI API key.":
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': 'No OpenAI API key provided. Please set your OpenAI API key in the settings.'
    })
    return HttpResponse('OpenAI API key not provided')

  if not transaction_data:
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': 'I can\'t understand your message. Please specify the amount and description of the transaction.'
    })
    return HttpResponse('Transaction not created')
  
  formatted_transaction_data = f"Transaction has been created: {transaction_data[0]['description']} with price {transaction_data[0]['amount']} {transaction_data[0]['transaction_currency']}."
  send_message("sendMessage", {
    'chat_id': chat_id,
    'text': formatted_transaction_data
  })
  
  return HttpResponse('Transaction created')

def send_message(method, data):
  return requests.post(os.getenv("TELEGRAM_BOT_API_URL") + method, data)