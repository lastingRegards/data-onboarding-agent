
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.retrieval import create_retrieval_chain

from langchain.chains.combine_documents import create_stuff_documents_chain


from ingestion import retriever




load_dotenv()


llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


get_bg = ChatPromptTemplate.from_messages(
    [("system", """You are an expert data integrator. You will be given information about a our account with a software 
      service, which will contain a link to its API landing page, our authentication information, and the account type.
        Reference our ontology and your background knowledge to determine what use case this product most likely serves 
        for us and thus what relevant data we can onboard from this service. Return ONLY the following:
        
        1. ALL authentication methods and their syntaxes
        2. The rate limit for our account (ex. 10 requests per 10 seconds)
        3. Pagination details, if applicable
        4. All base URLs used to make API calls
        5. For EVERY table in our ontology which has data we can onboard from this API return the following:
            - The API call method and endpoint necessary to batch query the data
            - Any parameters required by the API call
            - Response format received from call

        Your answer should be in markdown format and thorough enough that we will NOT need to reference the 
        documentation in order to retrieve ALL RELEVANT data.
    
        Our ontology is as follows: 
        {context}"""),
        ("human", "Service/Account information: {input}")]
)
    
test_prompt = ChatPromptTemplate.from_messages(
    [("system", """You are an expert data integrator. You will be given a link to a software service's API documentation,
        as well as the ontology of our company's current database. Based on background knowledge of the service, its given 
      documentation, and the Aden ontology, determine what tables in the ontology are relevant to this API.
        
        The ontology is as follows: 
        {context}"""),
        ("human", "External API documentation: {input}")]
    
)

stuff_documents_chain = create_stuff_documents_chain(llm, get_bg)

retrieve_chain = create_retrieval_chain(
    retriever=retriever, combine_docs_chain=stuff_documents_chain
) 
# result = qa.invoke(input={"input": query})







