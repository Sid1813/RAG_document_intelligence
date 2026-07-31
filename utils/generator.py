from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


def get_llm():
    return ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest",
        temperature=0,
    )


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

    if is_summary:

        prompt = f"""
You are an expert document analyst.

Your task is to summarize the document using ONLY the information provided below.

Do not invent facts.

If the document is incomplete, explicitly state that the summary is based only on the available pages.

Format your response exactly like this:

# Overview

A concise overview.

# Key Concepts

- Point 1
- Point 2
- Point 3

# Important Takeaways

- Takeaway 1
- Takeaway 2
- Takeaway 3

Context:

{context}
"""

    else:

        prompt = f"""
You are an expert AI document assistant.

Answer the user's question using ONLY the supplied document context.

Rules:

- Never make up information.
- If the answer cannot be found, reply:
"I couldn't find that information in the document."
- Keep the answer clear and well structured.
- Use bullet points when appropriate.
- Quote terminology from the document whenever useful.
- Do not mention "the provided context."
- Do not mention that you are an AI assistant.

Context:

{context}

Question:

{question}
"""

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return response.content