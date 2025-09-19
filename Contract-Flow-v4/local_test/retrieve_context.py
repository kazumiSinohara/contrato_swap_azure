from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
import os

# Load environment variables from .env file
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://telefonica-open-ai.openai.azure.com")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDINGS_MODEL = os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-large")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://contracts-v3-large.search.windows.net")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
PF_DISABLE_TRACING = "true"

os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_OPENAI_EMBEDDINGS_MODEL"] = AZURE_OPENAI_EMBEDDINGS_MODEL
os.environ["AZURE_SEARCH_ENDPOINT"] = AZURE_SEARCH_ENDPOINT
os.environ["AZURE_SEARCH_ADMIN_KEY"] = AZURE_SEARCH_ADMIN_KEY   

def retriever(questions: list[str], index_name: str, pdf_filename: str, k: int) -> str:
    filter_parameter = "contract_filename"
    #filter_parameter = "document_filename"

    # Embedding function
    aoai_embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL"),    
    )

    # Vector store setup
    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_ADMIN_KEY"),
        index_name=index_name,
        embedding_function=aoai_embeddings.embed_query,
    )

    # Combine questions into a single search query
    combined_query = "\n".join(questions)
    print("🔍 Consulta combinada:")
    print(combined_query)

    # Retrieve relevant docs the questions
    docs_and_scores = vector_store.similarity_search_with_relevance_scores(
        query=combined_query,
        k=k,
        filters=f"{filter_parameter} eq '{pdf_filename}'",
        score_threshold=0.5,
    )
    #docs_and_scores = vector_store.similarity_search("", k=1000, filters=f"{filter_parameter} eq '{pdf_filename}'")
    #breakpoint()

    retrieved_docs = {}
    #print('docs_and_scores', docs_and_scores)
    for doc, score in docs_and_scores:
        #print('doc', doc.page_content)
        retrieved_docs[doc.page_content] = score

    context = "\n\n".join(retrieved_docs.keys())
    return context

# Example usage
if __name__ == "__main__":
    questions = [
        "CNPJ/MF da empresa ITAKE",
    ]
    pdf_filename = "SWP FO TLF x ITAKE 001 2012 5.pdf.txt"
    print(pdf_filename)
    index = "contracts-v3-large"
    k = 5

    context = retriever(questions, index, pdf_filename, k)
    print("\n📄 Contexto Recuperado:\n")
    print(context)
