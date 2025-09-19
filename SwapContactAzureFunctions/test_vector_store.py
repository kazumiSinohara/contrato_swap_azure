from dotenv import load_dotenv
load_dotenv()
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)

documents = [Document(
    page_content="My document to try it out",
    metadata={"contract_filename": "contrato_swap_teste.pdf"}
)]

# insert into vector store
aoai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL"),  # deployment name, not model name!
)
print(f"Embedding model: {os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL')}")

my_index_fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=3072,  # <-- for text-embedding-3-large
        vector_search_profile_name="myHnswProfile",
    ),
    SearchableField(
        name="metadata",
        type=SearchFieldDataType.String,
    ),
    SimpleField(
        name="contract_filename",
        type=SearchFieldDataType.String,
        key=False,
        filterable=True,
    ),
    SimpleField(
        name="assignor",
        type=SearchFieldDataType.String,
        key=False,
        filterable=True,
    ),
    SimpleField(
        name="assignor_cnpj",
        type=SearchFieldDataType.String,
        key=False,
        filterable=True,
    ),
]

print(f"Vector store address: {os.getenv('VECTOR_STORE_ADDRESS')}")
print(f"Vector store password: {os.getenv('VECTOR_STORE_PASSWORD')}")
index_name: str = "contracts-v3"  # <-- use your new index name
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=os.getenv("VECTOR_STORE_ADDRESS"),
    azure_search_key=os.getenv("VECTOR_STORE_PASSWORD"),
    index_name=index_name,
    embedding_function=aoai_embeddings.embed_query,
    fields=my_index_fields
)

print(vector_store.add_documents(documents=documents))