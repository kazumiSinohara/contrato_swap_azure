import os
from langchain_core.documents import Document
from langchain.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents.indexes.models import (
                SearchableField,
                SearchField,
                SearchFieldDataType,
                SimpleField,
            )

documents = [Document(
                page_content="My document to try it our",
                metadata = {"contract_filename":"oiii.pdf"}
            )]

# insert into vector store
aoai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL"),
)

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
                vector_search_dimensions=1536, #text-embedding-ada-002
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

index_name: str = "contracts-v1"
vector_store: AzureSearch = AzureSearch( #if the index doesn't exist this command creates it
    azure_search_endpoint=os.getenv("VECTOR_STORE_ADDRESS"),
    azure_search_key=os.getenv("VECTOR_STORE_PASSWORD"),
    index_name=index_name,
    embedding_function=aoai_embeddings.embed_query,
    fields = my_index_fields
)
#print([f.name for f in vector_store.fields])
print(vector_store.add_documents(documents=documents))