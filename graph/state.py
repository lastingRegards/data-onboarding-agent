from typing import Annotated, Any
import operator
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


# For data formatting
class Table(BaseModel):
    """A table of data."""

    tableName: str = Field( ..., description="The tableName of the table")
    rows: list[dict[str,Any]] = Field(...,
                    description="""A list of rows of data in the table. Each row is a dict with columnName as
                    the key and cell value as the value.""")

class Tables(BaseModel):
    tables: list[Table] = Field(...,description="A list of tables")



###########################################################################################


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

    # service info: our account info, the API link, etc
    service: str

    # documentation summary/ontology mapping
    mapping: str

    # REACT agent's API calls raw response
    raw_data: str

    # final form of data needed
    data: Tables

    

