from dotenv import load_dotenv

load_dotenv()
import operator
from graph.state import State
from langchain_core.tools import tool
#from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode
#import pandas as pd
import requests
from typing import Annotated, List, TypedDict, Any, Union, Tuple
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langgraph.types import Send
from langchain.chat_models import init_chat_model
from ratelimit import limits
from langchain_core.runnables import RunnableConfig

llm = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)

# SCHEMA
# Schema for structured output to use in planning
# assumes one call per table
class Call(BaseModel):
    table: str = Field(
        description="tableName this endpoint matches to",
    )
    auth: str = Field(
        description="Authorization token and syntax for usage",
    )
    call: str = Field(
        description="Brief outline of API call syntax (base URL, endpoint, method, parameters) and pagination",
    )
    response: str = Field(
        description="Brief outline of response format of API call",
    )

class Calls(BaseModel):
    calls: list[Call] = Field(
        description="List of specs for each API call",
    )


class Table(BaseModel):
    tables: List[Union[list,dict]] = Field(
        description="List of JSON objects in list/dictionary form.",
    )




###########################################################################################
# TOOLS

@tool
@limits(calls=100, period=10)
def get_json_request(url:str, params:dict[str,Any], headers:dict[str,Any]) -> Union[dict,list]:
    '''Tool that calls HTTP get request using specified URL, params, and headers. Call must have JSON response format.'''
    print("---MAKING API CALL---")
    response = requests.get(url, params=params, headers=headers)
    return response.json()["results"]
tools = [get_json_request]
tool_node = ToolNode(tools)

"""
# pandas dataframe/conversion tools
def batch_to_dataframe(batch : list[dict]) -> pd.DataFrame:
    '''Takes a list of dictionary entries and converts each dictionary into a row in the resulting dataframe.'''
    pass
"""

############################################################################################

# Augment the LLM with schema for structured output
planner = llm.with_structured_output(Calls)


# Worker state
class WorkerState(MessagesState):
    #json_response: dict[str,Any] # unsure if need
    call_spec: Call
    raw_data: Annotated[list, operator.add]


# Orchestrator Node
def orchestrator(state: State):
    """Orchestrator that divides up API call workload"""

    # Generate queries
    calls_to_make = planner.invoke(
        [
            SystemMessage(content=f"Outline the specifications of each API call we need to make based off the mapping. Make sure to use the following token value when summarizing authorization: {state["service"]}."),
            HumanMessage(content=f"Here is the mapping: {state['mapping']}"),
        ]
    )
    return {"api_calls": calls_to_make.calls}



# worker agent 
worker_agent = create_react_agent(
    model=llm,
    tools=tools
)

# need to return answer as a huge list
def llm_call(state: WorkerState):
    """Worker makes API call"""
    call_spec = state["call_spec"]

    user_msg = f'''You are a data onboarder. You have been given the table {call_spec.table} to onboard data into
    using a given API call specification. Make a single call to the endpoint.
    Authorization: {call_spec.auth}
    Call Syntax: {call_spec.call}
    Response Syntax: {call_spec.response}
    '''

    # Generate section
    result = worker_agent.invoke(
            {"messages": [{"role": "user", "content": user_msg}]}
    )

    print(result)

    # Write the updated section to completed sections
    return {"messages": [result["messages"]]}


def synthesizer(state: State):
    """Synthesize full report from sections"""

    # List of completed sections
    raw_data = state["raw_data"]

    # Format completed section to str to use as context for final sections
    #completed_report_sections = "\n\n---\n\n".join(completed_sections)
    print(raw_data)
    return
    #return {"final_report": completed_report_sections}


# Conditional edge function to create llm_call workers that each write a section of the report
def assign_workers(state: State):
    """Assign a worker to each section in the plan"""

    # Kick off section writing in parallel via Send() API
    return [Send("llm_call", {"call_spec": c}) for c in state["api_calls"]]

########################################################################
### Tool node routing

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    messages = state["messages"]
    response = worker_agent.invoke(messages)
    return {"messages": [response]}

#######################################################################


# Build workflow
orchestrator_worker_builder = StateGraph(State)

# Add the nodes
orchestrator_worker_builder.add_node("orchestrator", orchestrator)
orchestrator_worker_builder.add_node("llm_call", llm_call)
orchestrator_worker_builder.add_node("synthesizer", synthesizer)
orchestrator_worker_builder.add_node("tools", tool_node)
orchestrator_worker_builder.add_node("call_model", call_model)
orchestrator_worker_builder.add_conditional_edges("llm_call", should_continue, ["tools", "synthesizer"])
orchestrator_worker_builder.add_conditional_edges("call_model", should_continue, ["tools", "synthesizer"])
orchestrator_worker_builder.add_edge("tools", "call_model")

# Add edges to connect nodes
orchestrator_worker_builder.add_edge(START, "orchestrator")
orchestrator_worker_builder.add_conditional_edges(
    "orchestrator", assign_workers, ["llm_call"]
)
orchestrator_worker_builder.add_edge("synthesizer", END)

# Compile the workflow
orchestrator_worker = orchestrator_worker_builder.compile()

# Invoke
#state = orchestrator_worker.invoke({"topic": "Create a report on LLM scaling laws"})

