## Data Onboarding Agent

credentials for account info is kept in a txt file in the main project directory, just for testing convenience.

Steps:
* use URL, check with stored credentials for matching account and return that info
* using URL, account info, and ontology, make summary of all API details needed to onboard data
    * currently, no more summary of transformations: should be able deduce from response fields
* Query API using all calls listed and gather all data
* Using all gathered data, then attempt to match


TODO:
- account lookup error handling
- cache lookup results and implement architecture to search for if previous results exist first
