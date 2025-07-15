from dotenv import load_dotenv

load_dotenv()
from typing import Any, Dict, Literal
from graph.state import State
from langchain_community.document_loaders import JSONLoader
from langgraph.graph import END
from graph.consts import RETRIEVE


from graph.chains.get_account import account_chain
from test_vars import CREDENTIAL_PATH

from langgraph.types import Command

def account(state: State) -> Command[Literal[RETRIEVE, END]]:
    print('---ACCOUNT LOOKUP---')
    url = state["service"]
    docs = JSONLoader(CREDENTIAL_PATH,".",text_content=False).load()
    res = account_chain.invoke({"accounts":docs, "url":url})
    res = res.result

    # validate results to direct graph flow:
    if(isinstance(res,str)):
        print("Failed to retrieve any account linked to this documentation.")
        return Command(goto=END)
    else:
        return Command(
            update={"service" : res.other_service_info, "access_token" : res.access_token},
            goto=RETRIEVE
        )




