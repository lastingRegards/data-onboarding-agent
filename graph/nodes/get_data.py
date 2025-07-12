from dotenv import load_dotenv

load_dotenv()
import operator
from graph.state import State
from langchain_core.tools import tool
#from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode
#import pandas as pd
import requests
from typing import Annotated, List, TypedDict, Any, Union, Tuple, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langgraph.types import Send
from langchain.chat_models import init_chat_model
from ratelimit import limits
from langchain_core.runnables import RunnableConfig
from pydantic import validate_call

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

class Table(BaseModel):
    name: str = Field(description="tableName of the table.")
    data:dict[str,list] = Field(
        description="A dictionary of column names (keys) mapped to a list of the column's values.",
        example={'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
    )

class Tables(BaseModel):
    tables:list[Table] = Field(
        description="A list of Table objects."
    )


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


############################################################################################

from langgraph.graph import add_messages
class WorkerState(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]


# worker agent 
worker_agent = create_react_agent(
    llm,
    tools=tools,
    response_format=Tables
)


########################################################################
### Tool node routing
'''
def should_continue(state: WorkerState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: WorkerState):
    messages = state["messages"]
    response = worker_agent.invoke(messages)
    return {"messages": [response]}

#######################################################################

# Build workflow
orchestrator_worker_builder = StateGraph(WorkerState)

# Add the nodes
orchestrator_worker_builder.add_node("tools", tool_node)
orchestrator_worker_builder.add_node("call_model", call_model)
orchestrator_worker_builder.add_conditional_edges("call_model", should_continue, ["tools", END])
orchestrator_worker_builder.add_edge("tools", "call_model")

# Add edges to connect nodes
orchestrator_worker_builder.add_edge(START, "call_model")

# Compile the workflow
orchestrator_worker = orchestrator_worker_builder.compile()

# Invoke
#state = orchestrator_worker.invoke({"topic": "Create a report on LLM scaling laws"})

'''