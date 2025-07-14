
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.retrieval import create_retrieval_chain

from langchain.chains.combine_documents import create_stuff_documents_chain
from pydantic import BaseModel, Field

from ingestion import retriever
import re
import json

from graph.state import State, Tables



load_dotenv()


llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")




format_data = ChatPromptTemplate.from_messages(
    [("system", """You are an expert data onboarder. You will be given lists of extracted data organized by
      object type, and you must transform and convert these lists into proper JSON format to prepare for 
      onboarding into our Acho ontology. 

      For each object, find the relevant table in our ontology it should map to. For each property of an object,
      attempt to map it to a column in the ontology table you found, and if you are unable to then exclude it
      from your results. Do NOT match any IDs to the _aden_id or _acho_id columns, and if no other suitable
      ID columns exist in the ontology table, exclude this ID from results. Output your answer as 
      a JSON that matches the given schema: ```json\n{schema}\n```.
      
      Make sure to wrap the answer in ```json and ``` tags. Your output should use the tableName and tableColumn 
      names (NOT their display names) found from our ontology. 
      
      Our ontology is as follows: 
        {context}"""),
        ("human", "{input}")]
).partial(schema=Tables.model_json_schema())



# extracts JSON embedded between ```json and ```, if multiple in string only extracts first
def extract_json(output: dict) -> list[dict]:

    text = output["answer"]
    pattern = r"```json(.*?)```"


    match = re.search(pattern, text, re.DOTALL)

    json_string = match.string
    json_string.strip()
    json_string = json_string[7:-3]

    try:
        return json.loads(json_string)
    except Exception:
        raise ValueError(f"Failed to parse JSON: {output["answer"]}")



stuff_documents_chain = create_stuff_documents_chain(llm, format_data)

data_format_chain = create_retrieval_chain(
    retriever=retriever, combine_docs_chain=stuff_documents_chain
) | extract_json


def format_data(state: State):
    print("---FORMATTING DATA---")
    res = data_format_chain.invoke(input={"input": state["raw_data"]})
    return {"data":res["tables"]}

