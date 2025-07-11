from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

llm = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)

prompt = ChatPromptTemplate([
    ("system", 
    '''Answer queries using only the following information about your accounts:
    {accounts}'''),
    ("user", 
    '''Given a link to a software service's API, determine if the API belongs to any of your accounts. If
    so, return all information you have on that account along with the link. If not, return the word only 'Fail'.
    Do not return any other text!
    
    API documentation link: {url}''')
])

account_chain = prompt | llm | StrOutputParser()


