from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from graph.state import State
from graph.consts import ACCOUNT, RETRIEVE, GET_DATA, MAPPER, MAKE_CALLS, TRANSFORM, ONBOARD
from graph.nodes import account, retrieve, get_data
from test_vars import URL

load_dotenv()

workflow = StateGraph(State)

workflow.add_node(ACCOUNT, account)
workflow.add_node(RETRIEVE, retrieve) # use get initial ontology, also use get API/account details later? might need router here
workflow.add_node(GET_DATA, get_data)
#workflow.add_node(MAPPER, mapper)
#workflow.add_node(MAKE_CALLS, make_calls)
#workflow.add_node(TRANSFORM)
#workflow.add_node(ONBOARD)

workflow.add_edge(START, ACCOUNT)
workflow.add_edge(ACCOUNT, RETRIEVE)
workflow.add_edge(RETRIEVE, GET_DATA)
workflow.add_edge(GET_DATA, END)

app = workflow.compile()
res = app.invoke(input={"service":URL})





