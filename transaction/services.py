import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import requests
import os
from useraccount.models import User
from .models import RecurringTransaction


dotenv.load_dotenv()

def ai_transaction_converter(human_message, system_message):
    chat = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0)
    messages = [
    SystemMessage(
        content=f'{system_message}'
    ),
    HumanMessage(content=human_message),
        ]
    return chat.invoke(messages)


def email_before_reccuring_transaction(user_id):

    user = User.objects.get(id=user_id)
    email, name = user.email, user.name

    recurring_transactions = RecurringTransaction.objects.filter(user_id=user_id)

    for transaction in recurring_transactions:
        description, amount, currency = transaction.description, transaction.amount, transaction.currency
    
    url = "https://app.loops.so/api/v1/transactional"

    if name is None:
        name = ""

    payload = {
        "transactionalId": "clwvbrtz901k0lb4dxysn046m",
        "email": email,
        "dataVariables": {
            "name": name,
            "description": description,
            "amount": amount,
            "currency": currency,
        }
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('LOOPS_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()