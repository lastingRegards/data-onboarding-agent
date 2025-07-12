from typing import Annotated, Optional
import operator
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

# For react agent
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

from langgraph.graph.message import add_messages


###########################################################################################


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

    # service info: our account info, the API link, etc
    service: str

    # documentation summary
    mapping: str

    # mapping

    # headers to use for authentication
    headers: Optional[dict[str,str]]

    # data to extract (maybe just leave in msgs)

    api_calls: list

    # REACT agent's API calls raw response
    raw_data: str

    # final form of data needed
    data: Tables

    

