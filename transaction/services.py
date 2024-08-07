import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import requests
import os
from datetime import datetime
from useraccount.models import User
from .models import RecurringTransaction

def ai_transaction_converter(human_message, system_message, api_key):

    llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0, api_key=api_key)
    chat = llm
    messages = [
    SystemMessage(
        content=f'{system_message}'
    ),
    HumanMessage(content=human_message),
        ]
    return chat.invoke(messages)

def ai_report_generator(human_message, system_message, api_key, previous_report):

    llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0, api_key=api_key)
    chat = llm
    messages = [
    SystemMessage(
        content=f'{system_message}. Previous report: {previous_report}'
    ),
    HumanMessage(content=f'Transactions: {human_message}'),
        ]
    return chat.invoke(messages)