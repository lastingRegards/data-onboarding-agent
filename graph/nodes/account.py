from dotenv import load_dotenv

load_dotenv()
from typing import Any, Dict
from graph.state import State
from langchain_community.document_loaders import JSONLoader

from graph.chains.get_account import account_chain
from main import credential_path

def account(state: State) -> Dict[str, Any]:
    print('---ACCOUNT LOOKUP---')
    url = state["service"]
    docs = JSONLoader(credential_path,".").load()
    res = account_chain.invoke({"accounts":docs, "url":url})
    return {"service" : res}



