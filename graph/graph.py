from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from graph.state import State
from graph.consts import ACCOUNT, RETRIEVE, MAPPER, MAKE_CALLS, TRANSFORM, ONBOARD
from graph.nodes import account, retrieve

#from graph.chains.answer_grader import answer_grader
#from graph.chains.hallucination_grader import hallucination_grader
#from graph.chains.router import RouteQuery, question_router
#from graph.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
#from graph.nodes import generate, grade_documents, retrieve, web_search

load_dotenv()

workflow = StateGraph(State)

workflow.add_node(ACCOUNT, account)
workflow.add_node(RETRIEVE, retrieve) # use get initial ontology, also use get API/account details later? might need router here
#workflow.add_node(MAPPER, mapper)
#workflow.add_node(MAKE_CALLS, make_calls)
#workflow.add_node(TRANSFORM)
#workflow.add_node(ONBOARD)

workflow.add_edge(START, ACCOUNT)
workflow.add_edge(ACCOUNT, RETRIEVE)
workflow.add_edge(RETRIEVE, END)

app = workflow.compile()





