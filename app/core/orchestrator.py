from app.agents.research_agent import research_agent
from app.agents.planner_agent import planner_agent
from app.core.llm import get_llm

llm = get_llm()

def detect_intent(query):
    query = query.lower()

    if "difference" in query or "compare" in query:
        return "comparison"
    elif "plan" in query or "roadmap" in query:
        return "plan"
    elif "brief" in query or "short" in query:
        return "short"
    elif query.startswith(("what is", "who is", "define")):
        return "fact"
    else:
        return "normal"


def multi_agent_system(query, chat_history=None):

    intent = detect_intent(query)

    context = ""
    if chat_history:
        for user, bot in chat_history:
            context += f"{user}\n{bot}\n"

    full_query = context + "\n" + query

    research = research_agent(full_query).content

    if intent == "plan":
        final = planner_agent(research).content
    else:
        prompt = f"""
        Answer the user's question directly.

        STRICT RULES:
        - Do NOT ask follow-up questions
        - Do NOT act confused
        - Do NOT include study plan
        - Keep answer concise

        Question:
        {query}

        Context:
        {research}
        """
        final = llm.invoke(prompt).content

    return {"response": final}