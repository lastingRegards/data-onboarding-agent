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



###########################################################################################


class State(TypedDict):
    # raw output of account chain, use to validate result
    account_results: ValidAccount

    # service info: our account info, the API link, etc
    service: str

    # access token used for API
    access_token: str

    # documentation summary/ontology mapping
    mapping: str

    # REACT agent's API calls raw response
    raw_data: str

    # final form of data needed
    data: Tables

    

