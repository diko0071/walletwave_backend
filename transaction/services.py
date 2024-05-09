import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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