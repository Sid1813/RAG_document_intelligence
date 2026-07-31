import streamlit as st

from utils.loader import load_pdf
from utils.splitter import split_documents
from utils.embeddings import get_embeddings
from utils.retriever import (
    create_vector_store,
    get_retriever,
    retrieve_documents,
)
from utils.generator import (
    get_llm,
    generate_answer,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📄",
    layout="wide",
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    max-width:1100px;
}

h1{
    text-align:center;
}

[data-testid="stSidebar"]{
    background-color:#111827;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {
    "retriever": None,
    "llm": None,
    "documents": None,
    "processed": False,
    "chat_history": [],
    "filename": "",
    "pages": 0,
    "chunks": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# HEADER
# ==========================================================

st.title("🤖 AI Document Assistant")

st.markdown("""
<center>

Ask intelligent questions about your PDFs using
<b>Retrieval-Augmented Generation (RAG)</b>

🟢 Gemini &nbsp;&nbsp;&nbsp;
🟢 LangChain &nbsp;&nbsp;&nbsp;
🟢 ChromaDB

</center>
""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("⚙️ Control Panel")

    st.divider()

    if st.session_state.processed:

        st.success("🟢 Document Ready")

        st.subheader("📄 Current Document")
        st.write(st.session_state.filename)

        st.divider()

        st.subheader("📊 Statistics")

        col1, col2 = st.columns(2)

        col1.metric("Pages", st.session_state.pages)
        col2.metric("Chunks", st.session_state.chunks)

        st.divider()

        st.subheader("🧠 Models")

        st.caption("Embedding Model")
        st.write("Gemini Embedding 001")

        st.caption("Language Model")
        st.write("Gemini Flash")

        st.divider()

        if st.button("📂 Upload New Document", use_container_width=True):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()

    else:

        st.info("Upload a PDF to begin.")

    st.divider()

    if st.button("🗑️ Reset Session", use_container_width=True):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()

# ==========================================================
# UPLOAD
# ==========================================================

if not st.session_state.processed:

    uploaded_file = st.file_uploader(
        "📂 Upload PDF",
        type=["pdf"]
    )

else:

    st.success(f"📄 Current Document: **{st.session_state.filename}**")

    uploaded_file = None

# ==========================================================
# PROCESS PDF
# ==========================================================

if uploaded_file is not None and not st.session_state.processed:

    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    progress = st.status(
        "Processing document...",
        expanded=True
    )

    progress.write("📄 Loading PDF...")

    documents = load_pdf("temp.pdf")

    progress.write("✂️ Splitting into chunks...")

    chunks = split_documents(documents)

    progress.write("🧠 Creating embeddings...")

    embeddings = get_embeddings()

    progress.write("🗄️ Building vector database...")

    vector_store = create_vector_store(
        chunks,
        embeddings,
    )

    retriever = get_retriever(vector_store)

    progress.write("🤖 Initializing Gemini...")

    llm = get_llm()

    progress.update(
        label="✅ Document Ready",
        state="complete",
    )

    st.session_state.documents = documents
    st.session_state.retriever = retriever
    st.session_state.llm = llm

    st.session_state.filename = uploaded_file.name
    st.session_state.pages = len(documents)
    st.session_state.chunks = len(chunks)

    st.session_state.processed = True

    st.success(f"""
📄 **{uploaded_file.name}**

✅ {len(documents)} pages loaded

✅ {len(chunks)} chunks created

✅ Vector database indexed

Ready for questions.
""")

    st.rerun()

# ==========================================================
# SUGGESTED QUESTIONS
# ==========================================================

if (
    st.session_state.processed
    and len(st.session_state.chat_history) == 0
):

    st.info("""
### 💡 Suggested Questions

• Summarize this document

• What is the main topic?

• Explain the key concepts.

• Give me the important takeaways.

• Explain this like I'm a beginner.
""")

# ==========================================================
# CHAT
# ==========================================================

if st.session_state.processed:

    question = st.chat_input(
        "Ask a question about your document..."
    )

    if question:

        summary_keywords = [
            "summary",
            "summarize",
            "summarise",
            "overview",
            "key points",
            "important takeaways",
            "main points",
        ]

        is_summary = any(
            keyword in question.lower()
            for keyword in summary_keywords
        )

        if is_summary:

            docs = st.session_state.documents[:30]

        else:

            docs = retrieve_documents(
                st.session_state.retriever,
                question,
            )

        answer = generate_answer(
            st.session_state.llm,
            question,
            docs,
        )

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
                "docs": docs,
            }
        )

        st.rerun()

# ==========================================================
# CHAT HISTORY
# ==========================================================

for chat in st.session_state.chat_history:

    with st.chat_message("user"):

        st.markdown(chat["question"])

    with st.chat_message("assistant"):

        st.markdown(chat["answer"])

        st.caption(
            f"🤖 Gemini Flash • 📚 {len(chat['docs'])} supporting passages"
        )

        with st.expander("📚 Sources Used"):

            for doc in chat["docs"]:

                page = doc.metadata.get("page", "Unknown")

                st.markdown(f"### 📄 Page {page}")

                st.write(doc.page_content)

                st.divider()