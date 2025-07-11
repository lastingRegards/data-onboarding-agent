## Data Onboarding Agent

credentials for account info is kept in a txt file in the main project directory, just for testing convenience.

Steps:
* use URL, check with stored credentials for matching account and return that info
* using URL, account info, and ontology, make summary of all API details needed to onboard data
    * currently, no more summary of transformations: should be able deduce from response fields
* Query API using all calls listed and gather all data
    * try to summarize this in pandas format, can transform using python repl tools
* Using all gathered data, then attempt to match



PRIMARY TODOs:
* tool calling and configuring dynamic tools
https://langchain-ai.github.io/langgraph/how-tos/tool-calling/#configuration
* rate limiting
https://python.langchain.com/docs/how_to/chat_model_rate_limiting/


TODO:
- account lookup error handling
- cache lookup results and implement architecture to search for if previous results exist first
