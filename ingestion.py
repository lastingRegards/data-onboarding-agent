from dotenv import load_dotenv

load_dotenv()

from langchain_text_splitters import RecursiveJsonSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from main import PINECONE_INDEX

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def ingest_json(path:str):
    loader = JSONLoader(
    file_path=path,
    jq_schema=".",
    text_content=False
)

    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    docs = splitter.split_documents(raw_docs)

    print(f"Going to add {len(docs)} to Pinecone")
    PineconeVectorStore.from_documents(
        docs, embeddings, index_name="aden-rag"
    )
    print("****Loading to vectorstore done ***")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
docsearch = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
retriever=docsearch.as_retriever()


if __name__ == "__main__":
    #path = ""
    #ingest_json(path)
    pass