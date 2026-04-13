from app.agents.research_agent import research_agent
from app.agents.planner_agent import planner_agent
from app.core.llm import get_llm

llm = get_llm()

def generate_title(user_input):
    prompt = f"""
    Generate a short chat title (max 4 words).

    STRICT RULES:
    - Only return the title
    - No punctuation
    - No extra words

    Input:
    {user_input}
    """

    title = llm.invoke(prompt).content.strip()
    title = title.replace("Title:", "").strip()
    title = title.replace('"', '').strip()
    title = title.split("\n")[0]

    return title[:40]


def detect_intent(query):
    query = query.lower()

    if "difference" in query or "compare" in query:
        return "comparison"
    elif "plan" in query or "roadmap" in query:
        return "plan"
    else:
        return "normal"


def multi_agent_system(query, chat_history=None, mode="normal"):

    context = ""
    if chat_history:
        for user, bot in chat_history:
            context += f"{user}\n{bot}\n"

    full_query = context + "\n" + query

    research = research_agent(full_query).content

    intent = detect_intent(query)

    if intent == "plan":
        final = planner_agent(research).content

    else:
        prompt = f"""
        Answer the user's question.

        STYLE:
        - Mode: {mode}

        RULES:
        - If mode is short → answer in 2-3 lines
        - If mode is detailed → explain properly
        - If mode is normal → balanced answer
        - Do NOT include study plan unless asked
        - Do NOT ask follow-up questions

        Question:
        {query}

        Context:
        {research}
        """

        final = llm.invoke(prompt).content

    return {"response": final}