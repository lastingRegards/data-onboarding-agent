# Data Onboarding Agent

## Setup
### pipenv
pipenv is used to manage the virtual environment for this project. After cloning the git repository, run the following in the project directory:
```bash
# Install dependencies including development packages
$ pipenv install --dev

# Activate the virtual environment
$ pipenv shell
```
From here, you should be able to run the project as normal using `python`. To exit the virtual environment, use `exit`.

### Javascript
Project also requires use of the Acho Javascript SDK for Node.js. This can be installed as follows: 
```bash
$ npm install @acho-inc/acho-js
```

### Required .env keys
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `PINECONE_API_KEY`
- `LANGCHAIN_API_KEY`
- `ACHO_TOKEN`

### Testing Variables
These can be found and set in `test_vars.py` for testing purposes.
- `CREDENTIAL_PATH`: path to the credentials JSON folder for account credentials of services we are onboarding data from. An example of this file is provided at `example_credentials.json`.
- `PINECONE_INDEX`: name of the Pinecone index used to store the vector database for this project. 
- `URL`: URL of documentation for service we are onboarding from.

### Pinecone DB
Pinecone DB is in `text-embedding-3-small` format with 1536 dimensions. This stores a JSON file of the ontology being onboarded to. The `ingestion.py` file was called to embed the ontology file, see this for more details.



## Outline
Currently, the project takes in a URL to a documentation page and from there works to find and onboard all relevant data stored by the account the user has with this service, which should be defined in a JSON file storing the credentials.
- START: **URL** passed in as input 
- **account:** references the stored **credentials** (currently just in untracked text file for testing purposes) against **URL**, adds information about account to state (token, tier, etc)
- **retrieve:** takes account info and looks up ontology stored in Pinecone VectorDB, makes **mapping** of all tables can onboard to and API call specifications for doing so
- **get_data:** Makes API calls to retrieve all data possible based off the calls specified in 
**mapping**.
    - currently: no OAUTH, only GET requests with JSON return format implemented
- **format_data:** Takes raw output of making API calls and converts into JSON format, mapping to data to proper tables and excluding columns not already in ontology.
- **onboard:** Takes formatted data to onboard and loads it into Aden.



## In Progress
- **More thorough API scraping:** Keep AI from hallucinating documentation and be more thorough in scraping relevant endpoints.
- **Data processing/transformation:** Currently, data is simply read in from API endpoints and then passed into the Aden system. Need to process data, identify relationships, and perform necessary transformations for more thorough onboarding.
- **Error handling:** Incorrect/extra columns in onboarding can result in the entire table of data not being uploaded, needs to be addressed. More refinement of AI workflow needed in general to validate responses and prevent errors.
- **Refine onboarding:** Ensure onboarding data is not resulting in duplicate entries, ignore these values or possibly consider allowing onboarded data to update previous entries.
- **Optimizing workflow:** Current AI agent workflow is entirely sequential, should make use of parallelization/splitting tasks between multiple agents when possible. 
- **Project file organization:** Clean up the structure of project files structure, a lot of dead/debug code still left in, consider combining chain and node files.



## Implementation Notes/Design Decisions
- **Data to onboard:** System currently operates under assumption that all relevant data from user's account should be onboarded. Possible alternatives:
    - Consider prompting user for what data should be onboarded before scraping to better inform API scrape
    - Could scrape for all API endpoints, then prompt user to choose which should be used for onboarding
- **ID handling:** Uncertain if aden/acho IDs should be set by external services/if they are internally assigned by Aden system, so current implementation avoids populating these IDs as importing from multiple different platforms could possibly result in ID conflicts. Possible alternatives:
    - Allow onboarded data to assign an ID value (either acho or aden) if this entry can't be tied to an existing ID value.


