from typing import Any, Dict

from graph.state import State
from graph.chains.retrieval import retrieve_chain


def retrieve(state: State) -> Dict[str, Any]:
    print("---RETRIEVE---")
    service = state["service"]

    res = retrieve_chain.invoke(input={"input": service})

    return {"mapping": res['answer'], "service":service}