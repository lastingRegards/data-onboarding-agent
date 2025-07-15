from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from graph.state import State
from graph.consts import ACCOUNT, RETRIEVE, GET_DATA, FORMAT_DATA, ONBOARD
from graph.nodes import account, retrieve, get_data, format_data, onboard
from graph.nodes.get_data import orchestrate, assign_workers
from test_vars import URL

load_dotenv()

workflow = StateGraph(State)

workflow.add_node(ACCOUNT, account)
workflow.add_node(RETRIEVE, retrieve) # use get initial ontology, also use get API/account details later? might need router here
workflow.add_node("orchestrate", orchestrate)
workflow.add_node(GET_DATA, get_data)
#workflow.add_node(FORMAT_DATA, format_data)
workflow.add_node(ONBOARD, onboard)

workflow.add_edge(START, ACCOUNT) # Account uses Command to handle flow to either retrieve or end
#workflow.add_edge(ACCOUNT, RETRIEVE)
workflow.add_edge(RETRIEVE, "orchestrate")
workflow.add_conditional_edges(
    "orchestrate", assign_workers, [GET_DATA]
)
#workflow.add_edge(GET_DATA, FORMAT_DATA)
#workflow.add_edge(FORMAT_DATA, ONBOARD)
workflow.add_edge(ONBOARD, END)

app = workflow.compile()





