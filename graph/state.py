from typing import Annotated, Any, Union
import operator
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

# For account results formatting
class Account(BaseModel):
    """Information on an account."""

    access_token: str = Field( ..., description="The access token of the account.")
    other_service_info: str = Field(...,
                    description="""All outputs requested, including the token/token type.""")

class ValidAccount(BaseModel):
    result: Union[str,Account] = Field( ..., description="The Account information if successfully found, otherwise just return 'Fail'.")

##################################################################################################

# For data formatting
class Table(BaseModel):
    """A table of data."""

    tableName: str = Field( ..., description="The tableName of the table")
    rows: list[dict[str,Any]] = Field(...,
                    description="""A list of rows of data in the table. Each row is a dict with columnName as
                    the key and cell value as the value.""")

class Tables(BaseModel):
    tables: list[Table] = Field(...,description="A list of tables")

class Call(BaseModel):
    base_url: str = Field(
        description="The base URL for this API call.",
    )
    endpoint: str = Field(
        description="The endpoint of this API call.",
    )
    pagination: str = Field(
        description="Description of how to handle pagination for this API call.",
    )
    access_token: str = Field(
       description="The access token value needed to make the API call (if exists).",
    )
    headers: str = Field(
        description="Description of what headers should be used for this API call.",
    )
    parameters: str = Field(
        description="Description of what parameters can be used for this API call.",
    )
    response_schema: str = Field(
        description="An description of the response schema to expect from this API call.",
    )
  
class Calls(BaseModel):
    calls: list[Call] = Field(
        description="List of API calls to be made.",
    )

class WorkerState(TypedDict):
   access_token: str
   call: Call
   raw_endpoint: str
   data : Annotated[list[Table], operator.add]

###########################################################################################


class State(TypedDict):
    # service info: our account info, the API link, etc
    service: str

    # access token used for API
    access_token: str

    # documentation summary/ontology mapping
    mapping: str

    # REACT agent's API calls raw response
    raw_data: str

    # final form of data needed
    data: Annotated[list[Table], operator.add]

    # description of API calls to make
    calls: Calls

    

