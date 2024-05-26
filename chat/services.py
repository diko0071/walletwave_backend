import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

dotenv.load_dotenv()

def ai_reponse(human_message, system_message, previous_messages):
    chat = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0)
    messages = [
    SystemMessage(
        content=f'{system_message}. Previous messages: {previous_messages}'
    ),
    HumanMessage(content=human_message),
        ]
    return chat.invoke(messages)


def create_ai_title_for_session(previous_messages):
    chat = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0)
    system_message = 'Your goal is create chat name based on previous message. The chat name should be summary of the previous messages requests. It should be NOT more than 3-4 words. BE VERY CONSICE AND SHORT, but in the same time be very obverse and create name which will explain what is the topic of the chat'
    messages = [
    SystemMessage(
        content=f'{system_message}'
    ),
    HumanMessage(content=f'Previous messages: {previous_messages}'),
        ]
    return chat.invoke(messages)

