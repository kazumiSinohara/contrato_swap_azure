from promptflow import tool
import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def retriever(question: str, index: str, pdf_filename: str, k: int) -> str:
    if index == "contracts":
        index_name: str = "contracts-v1"
        filter_parameter = "contract_filename"
    elif index == "swap":
        index_name: str = "swap-v1"
        filter_parameter = "document_filename"
    else:
        raise ValueError(f"No index for {index}")

    aoai_embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL"),
        #openai_api_version="<Azure OpenAI API version>",  # e.g., "2023-12-01-preview"
    )

    vector_store: AzureSearch = AzureSearch( 
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_ADMIN_KEY"),
        index_name=index_name,
        embedding_function=aoai_embeddings.embed_query,
    )

    #retriever_filter = vector_store.as_retriever(search_type="similarity", k = 3, search_kwargs={"filters": f"contract_filename eq '{contract_pdf}'"})
    #result = retriever_filter.invoke(question)

    docs_and_scores = vector_store.similarity_search_with_relevance_scores(
        query=question,
        k=k,
        filters = f"{filter_parameter} eq '{pdf_filename}'",
        score_threshold=0.70,
    )

    def _format_docs(docs):
        return "\n\n".join(doc[0].page_content for doc in docs)

    context = _format_docs(docs_and_scores)
    return context