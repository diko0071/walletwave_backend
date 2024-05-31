import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .prompts import text_to_sql_prompt, question_validation_prompt


dotenv.load_dotenv()

llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0)

def ai_reponse(human_message, system_message, previous_messages=None):
    chat = llm
    messages = [
    SystemMessage(
        content=f'{system_message}. Previous messages: {previous_messages}'
    ),
    HumanMessage(content=human_message),
        ]
    return chat.invoke(messages)


def create_ai_title_for_session(previous_messages):
    chat = llm
    system_message = 'Your goal is create chat name based on previous message. The chat name should be summary of the previous messages requests. It should be NOT more than 3 WORDS ONLY. BE VERY CONSICE AND SHORT, but in the same time be very obverse and create name which will explain what is the topic of the chat'
    messages = [
    SystemMessage(
        content=f'{system_message}'
    ),
    HumanMessage(content=f'Previous messages: {previous_messages}'),
        ]
    return chat.invoke(messages)

def text_to_sql(human_message, user_id):
    system_message = text_to_sql_prompt
    question = human_message

    sql_query = ai_reponse(question, system_message)

    return sql_query

def validate_question(human_message):
    system_message = question_validation_prompt
    question = human_message

    answer = ai_reponse(question, system_message)

    return int(answer.content)