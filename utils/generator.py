from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# ==========================================================
# LOAD LLM
# ==========================================================

def get_llm():

    return ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest",
        temperature=0,
    )


# ==========================================================
# GENERATE ANSWER
# ==========================================================

def generate_answer(llm, question, documents):

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    question_lower = question.lower()

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
        keyword in question_lower
        for keyword in summary_keywords
    )

    # ------------------------------------------------------
    # SUMMARY PROMPT
    # ------------------------------------------------------

    if is_summary:

        prompt = f"""
You are an expert document analyst.

Summarize the document using ONLY the information below.

Never invent information.

If the document is incomplete, clearly mention that the summary is based only on the available pages.

Return your answer in Markdown.

# Overview

Provide a concise overview.

# Key Concepts

- Point 1
- Point 2
- Point 3

# Important Takeaways

- Takeaway 1
- Takeaway 2
- Takeaway 3

Document Context:

{context}
"""

    # ------------------------------------------------------
    # QUESTION ANSWERING PROMPT
    # ------------------------------------------------------

    else:

        prompt = f"""
You are an expert AI document assistant.

Answer the user's question using ONLY the supplied document.

Rules:

- Never hallucinate.
- Never invent facts.
- If the answer is missing, reply:
"I couldn't find that information in the document."
- Use headings and bullet points whenever appropriate.
- Keep answers concise but informative.
- Do NOT mention "the provided context".
- Do NOT mention you are an AI.

Document Context:

{context}

Question:

{question}
"""

    # ------------------------------------------------------
    # CALL GEMINI
    # ------------------------------------------------------

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    # ------------------------------------------------------
    # RETURN ONLY THE TEXT
    # ------------------------------------------------------

    if hasattr(response, "text") and response.text:
        return response.text

    if isinstance(response.content, str):
        return response.content

    if isinstance(response.content, list):

        answer = ""

        for block in response.content:

            # New LangChain format
            if hasattr(block, "text"):
                answer += block.text

            # Dictionary format
            elif isinstance(block, dict):

                if block.get("type") == "text":
                    answer += block.get("text", "")

        return answer.strip()

    return str(response.content)