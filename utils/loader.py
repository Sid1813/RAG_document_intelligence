from langchain_community.document_loaders import PyPDFLoader


def load_pdf(pdf_path):
    """
    Loads a PDF and returns a list of LangChain Document objects.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    return documents