from dotenv import load_dotenv

load_dotenv()
import operator
from graph.state import State, Table, Tables, Call, Calls, WorkerState
from langchain_core.tools import tool
#from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode
import pandas as pd
import requests
from typing import Annotated, List, TypedDict, Any, Union, Tuple, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langgraph.types import Send
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from ratelimit import limits
from langchain_core.runnables import RunnableConfig
from pydantic import validate_call

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

###########################################################################################
# TOOLS

@tool
@validate_call
@limits(calls=100, period=10)
def get_json_request(url:str, params:Optional[dict[str,Any]], headers:Optional[dict[str,Any]]) -> Union[dict,list]:
    '''Tool that calls HTTP get request using specified URL, params, and headers. 
    Call must have JSON response format.'''
    print("---MAKING API CALL---")
    print(f'url: {url}\nheaders: {headers}\nparams: {params}')
    response = requests.get(url, params=params, headers=headers)
    return response.json()["results"]

tools = [get_json_request]
tool_node = ToolNode(tools)

#########################################################################################################

def orchestrate(state: State):
  print("---ORCHESTRATING---")

  structured_llm = llm.with_structured_output(Calls)
  prompt = ChatPromptTemplate.from_messages(
      [("system", """You will be given a list of API calls that need to be made. Format the information
        needed for each API call based off the given output format, making sure to be very detailed
        in describing exactly what is needed for each call (ex. if you are given a specific token value 
        to use make sure to use it instead of a placeholder). Do not include optional parameters used 
        solely to filter the data/properties received."""),
        ("human", "{input}")]
  )
  chain = prompt | structured_llm
  res = chain.invoke({"input":state["mapping"]})
  print(res)
  return {'calls' : res.calls}

def assign_workers(state: State):
   # Make API calls in parallel using Send
    return [Send("get_data", {"call": c, "access_token":state["access_token"]}) for c in state["calls"]]

############################################################################################

# worker agent 
worker_agent = create_react_agent(
    llm,
    tools=tools
)


# node
def get_data(state: WorkerState):
    print("---FETCHING DATA---")
    token = state["access_token"]
    call = state["call"]
    user_msg = f'''You are a data analyst. You have been given a description of an API endpoint to make calls to 
    in order to onboard data into our database. Make API calls to retrieve ALL data from the given endpoint,
    making sure you are using VALID AUTHORIZATION, HEADERS, AND PARAMETERS for each call made.
    If you run into an error making the call, try once again and then assume there is an issue with the 
    endpoint and quit. If the "after" cursor is the same as received from a previous call OR if the same 
    data is retrieved after pagination, assume you have read all data and quit. 
    
    Print out all retrieved data as a table, or if no data was retrieved print "Fail" and NOTHING ELSE.
    
    Access Token: \n\n{token}\n\n
    API Call Description: \n\n{call}\n\n
    '''

    result = worker_agent.invoke({"messages":[{"role": "user", "content": user_msg}]})
    raw_endpoint = result["messages"][-1].content

    if (raw_endpoint == "Fail"):
        return Command(goto=END)
    
    docs = docsearch.similarity_search(raw_endpoint,k=2)
    

    format_data = ChatPromptTemplate.from_messages(
        [("system", """You are an expert data onboarder. You will be given lists of extracted data objects, and you must 
        transform and convert these lists into proper JSON format to prepare for onboarding into our Acho ontology
        if possible. 

        For each object, find the relevant table in our ontology it should map to. For each property of an object,
        attempt to map it to a column in the ontology table you found, and if you are unable to then exclude it
        from your results. Do NOT match any IDs to the _aden_id or _acho_id columns, and if no other suitable
        ID columns exist in the ontology table, exclude this ID from results. If you can successfully
        format the data, output your answer as a JSON that matches the given schema: ```json\n{schema}\n```, do NOT
        include the schema itself in your answer and do NOT include any additional text. If you were unable to format the data,
        return ONLY the word 'Fail'. Do NOT output any additional text.
        
        Make sure to wrap the answer in ```json and ``` tags. Your output should use the tableName and tableColumn 
        names (NOT their display names) found from our ontology. ENSURE THAT ALL COLUMNS IN YOUR RESPONSE EXIST
        IN OUR ONTOLOGY.
        
        Our ontology is as follows: 
            {context}"""),
            ("human", "{input}")]
    ).partial(schema=Table.model_json_schema())

    stuff_documents_chain = create_stuff_documents_chain(llm, format_data)
    data_format_chain = stuff_documents_chain | extract_json

    res = data_format_chain.invoke(input={"input": raw_endpoint, "context": docs})
    if (res == ""):
        return Command(goto=END)
    else:
        return Command(update={"data":[res]}, goto="onboard")


#########################################################################################################

import re
import json
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from ingestion import retriever, docsearch
from langgraph.types import Command
import subprocess
# extracts JSON embedded between ```json and ```, if multiple in string only extracts first
def extract_json(output: dict) -> list[dict]:

    text = output
    pattern = r"```json(.*?)```"


    match = re.search(pattern, text, re.DOTALL)

    try:
        json_string = match.string
        json_string.strip()
        json_string = json_string[7:-3]
        return json.loads(json_string)
    except Exception:
        print(f"Failed to parse JSON from: {output}")
        return ""

# formatting data
def format_data(state: WorkerState):
    print("---FORMATTING DATA---")
    format_data = ChatPromptTemplate.from_messages(
        [("system", """You are an expert data onboarder. You will be given lists of extracted data objects, and you must 
        transform and convert these lists into proper JSON format to prepare for onboarding into our Acho ontology. 

        For each object, find the relevant table in our ontology it should map to. For each property of an object,
        attempt to map it to a column in the ontology table you found, and if you are unable to then exclude it
        from your results. Do NOT match any IDs to the _aden_id or _acho_id columns, and if no other suitable
        ID columns exist in the ontology table, exclude this ID from results. Output your answer as 
        a JSON that matches the given schema: ```json\n{schema}\n```.
        
        Make sure to wrap the answer in ```json and ``` tags. Your output should use the tableName and tableColumn 
        names (NOT their display names) found from our ontology. 
        
        Our ontology is as follows: 
            {context}"""),
            ("human", "{input}")]
    ).partial(schema=Table.model_json_schema())

    stuff_documents_chain = create_stuff_documents_chain(llm, format_data)
    data_format_chain = create_retrieval_chain(
        retriever=retriever, combine_docs_chain=stuff_documents_chain
    ) | extract_json

    res = data_format_chain.invoke(input={"input": state["raw_endpoint"]})
    if (res == ""):
        return Command(goto=END)
    else:
        return Command(update={"data":[json.loads(res)]}, goto="synthesizer")

def synthesizer(state:State):
    print("---ONBOARDING DATA---")

    for args in state["data"]:
      print(args)
    
    return {}




########################################################################
### Routing
'''orchestrator_worker_builder = StateGraph(State)
orchestrator_worker_builder.add_node("orchestrate", orchestrate)
orchestrator_worker_builder.add_node("get_data", get_data)
#orchestrator_worker_builder.add_node("format_data", format_data)
orchestrator_worker_builder.add_node("synthesizer", synthesizer)

# Add edges to connect nodes
orchestrator_worker_builder.add_edge(START, "orchestrate")
orchestrator_worker_builder.add_conditional_edges(
    "orchestrate", assign_workers, ["get_data"]
)
#orchestrator_worker_builder.add_edge("get_data", "format_data")
orchestrator_worker_builder.add_edge("synthesizer", END)
test_graph = orchestrator_worker_builder.compile()'''

