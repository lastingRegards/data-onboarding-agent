from dotenv import load_dotenv

load_dotenv()
import operator
from graph.state import State, Table, Tables
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



class WorkerState(MessagesState):
    mapping : str
    service : str
    final_answer : Tables


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

dfs = dict()
class MakeDfSchema(BaseModel):
    """Makes a pandas dataframe for a given table with specified data."""
    name: str = Field(description="Table name")
    data: dict[str,list] = Field(
        description="Dictionary of table data, keyed by column name with values being a list of the column's data."
        )

@tool("make_dataframe", args_schema=MakeDfSchema)
def make_dataframe(name:str, data:dict):
    print(f"---MAKING DATAFRAME: {name}---")
    table = pd.DataFrame.from_dict(data, orient='index')
    dfs[name] = table


tools = [get_json_request]
tool_node = ToolNode(tools)


############################################################################################

# worker agent 
worker_agent = create_react_agent(
    llm,
    tools=tools
)


# node
def get_data(state: State):
    print("---FETCHING DATA---")
    service = state["service"]
    mapping = state["mapping"]
    user_msg = f'''You are a data analyst. You have been given a description of API calls to make in order
    to onboard data into our database. Make API calls to retrieve all data based on the given description,
    making sure you are using VALID AUTHORIZATION, HEADERS, AND PARAMETERS for each call made.
    If you run into an error making the call, try once again and then assume there is an issue with the 
    endpoint and move on to the next endpoint.
    Account Specifications: \n\n{service}\n\n
    Mapping: \n\n{mapping}\n\n
    '''

    '''
    for message_chunk, metadata in worker_agent.stream({"messages":[{"role": "user", "content": user_msg}]}, stream_mode="messages"):
        if message_chunk.content:
            print(message_chunk.content, end="", flush=True)
    '''

    result = worker_agent.invoke({"messages":[{"role": "user", "content": user_msg}]})
    raw_data = result["messages"][-1].content
    return {"raw_data":raw_data}




def cleaner_node(state : State):
    cleaner_llm = llm.with_structured_output(Tables)
    prompt_template = ChatPromptTemplate([
    ("system", "You will be given the raw output of an AI agent's API calls. Parse and return the data in this response into a structured format as defined."),
    ("user", "{raw_data}")
])
    cleaner_chain = prompt_template | cleaner_llm
    result = cleaner_chain.invoke({"raw_data" : state["raw_data"]})
    return {"data": result}



#######################################################################
# structured output


########################################################################
### Subgraph Node



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