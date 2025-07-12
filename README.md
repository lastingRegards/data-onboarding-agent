# Data Onboarding Agent

## Setup
### Required .env keys
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `PINECONE_API_KEY`
- `LANGCHAIN_API_KEY`

## Testing Variables
These can be found and set in `main.py` for testing purposes.
- `CREDENTIAL_PATH`: path to the credentials JSON folder for account credentials of services we are onboarding data from. An example of this file is provided at `example_credentials.json`.
- `PINECONE_INDEX`: name of the Pinecone index used to store the vector database for this project. 
- `URL`: URL of documentation for service we are onboarding from.

### Pinecone DB
Pinecone DB is in `text-embedding-3-small` format with 1536 dimensions. This stores a JSON file of the ontology being onboarded to. The `ingestion.py` file was called to embed the ontology file, see this for more details.


## Outline
- START: **URL** passed in as input 
- **account:** references the stored **credentials** (currently just in untracked text file for testing purposes) against **URL**, adds information about account to state (token, tier, etc)
- **retrieve:** takes account info and looks up ontology stored in Pinecone VectorDB, makes **mapping** of all tables can onboard to and API call specifications for doing so

- **api_call:** Uses **mapping** to orchestrate worker agents. Each worker agent is assigned an API endpoint to query all data from.
    - currently: no OAUTH, only GET requests with JSON return format implemented
    - consider implementing rate limits to API call
    - consolidating: once a worker is all done, they should add their cumulative data to list in the form of (tableName, [list of all json objects retrieved])

