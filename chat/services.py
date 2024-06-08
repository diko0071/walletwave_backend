import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .prompts import text_to_sql_prompt, question_validation_prompt

def ai_reponse(human_message, system_message, api_key, previous_messages=None):

    llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0, api_key=api_key)
    chat = llm
    messages = [
    SystemMessage(
        content=f'{system_message}. Previous messages: {previous_messages}'
    ),
    HumanMessage(content=human_message),
        ]
    return chat.invoke(messages)


def create_ai_title_for_session(previous_messages, api_key):
    llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0, api_key=api_key)
    chat = llm
    system_message = 'Your goal is create chat name based on previous message. The chat name should be summary of the previous messages requests. It should be NOT more than 3 WORDS ONLY. BE VERY CONSICE AND SHORT, but in the same time be very obverse and create name which will explain what is the topic of the chat'
    messages = [
    SystemMessage(
        content=f'{system_message}'
    ),
    HumanMessage(content=f'Previous messages: {previous_messages}'),
        ]
    return chat.invoke(messages)

def validate_question(human_message, api_key):
    system_message = question_validation_prompt
    question = human_message

    answer = ai_reponse(question, system_message, api_key)

    return int(answer.content)

