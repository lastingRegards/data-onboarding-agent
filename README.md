# Data Onboarding Agent

credentials for account info is kept in a txt file in the main project directory, just for testing convenience.

## Outline
- START: **URL** passed in as input 
- **account:** references the stored **credentials** (currently just in untracked text file for testing purposes) against **URL**, adds information about account to state (token, tier, etc)
- **retrieve:** takes account info and looks up ontology stored in Pinecone VectorDB, makes **mapping** of all tables can onboard to and API call specifications for doing so

- **api_call:** Uses **mapping** to orchestrate worker agents. Each worker agent is assigned an API endpoint to query all data from.
    - currently: no OAUTH, only GET requests with JSON return format implemented
    - consider implementing rate limits to API call
    - consolidating: once a worker is all done, they should add their cumulative data to list in the form of (tableName, [list of all json objects retrieved])

