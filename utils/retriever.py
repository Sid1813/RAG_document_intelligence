from langchain_chroma import Chroma


def create_vector_store(chunks, embeddings):
    """
    Creates a Chroma vector database from document chunks.
    """

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vector_db"
    )

    return vector_store


def get_retriever(vector_store):
    """
    Returns a retriever for similarity search.
    """

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever

def retrieve_documents(retriever, query):
    """
    Retrieves relevant documents for a given query.
    """

    return retriever.invoke(query)