import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .prompts import text_to_sql_prompt
from supabase import create_client, Client
from langchain.agents import create_tool_calling_agent


dotenv.load_dotenv()

client = create_client()

llm = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0)

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


def execute_sql_query(sql_query, user_id):
    sql_query = sql_query.replace("WHERE", f"WHERE user_id = '{user_id}' AND")

    result = client.sql.execute(sql_query)
    return result

def text_to_sql(human_message, user_id):
    system_message = text_to_sql_prompt
    question = human_message

    sql_query = ai_reponse(question, system_message)

    result = execute_sql_query(sql_query, user_id)

    return result