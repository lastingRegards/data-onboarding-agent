from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Union

llm = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)

# For account results formatting
class Account(BaseModel):
    """Information on an account."""

    access_token: str = Field( ..., description="The access token of the account.")
    other_service_info: str = Field(...,
                    description="""All other output requested.""")

class ValidAccount(BaseModel):
    result: Union[str,Account] = Field( ..., description="The Account information if successfully found, otherwise just return 'Fail'.")

structured_llm = llm.with_structured_output(ValidAccount)

prompt = ChatPromptTemplate([
    ("system", 
    '''Answer queries using only the following information about your accounts:
    {accounts}'''),
    ("user", 
    '''Given a link to a software service's API, determine if the API belongs to any of your accounts. If
    so, return all information you have on that account along with the given API link and a short description of what
    use case the service fulfills/what kind of data it might store. If not, return the word only 'Fail'.
    Do not return any other text!
    
    API documentation link: {url}''')
])

account_chain = prompt | structured_llm #| StrOutputParser()


