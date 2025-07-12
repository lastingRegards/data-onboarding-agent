from graph.graph import app


## TESTING VARIABLES
CREDENTIAL_PATH = "./credentials.json"
PINECONE_INDEX = "aden-rag"
URL = "https://developers.hubspot.com/docs/reference/api/overview"


########################################################################################

# MAIN APP CALL
print(app.invoke(input={"service":URL})["service"])
