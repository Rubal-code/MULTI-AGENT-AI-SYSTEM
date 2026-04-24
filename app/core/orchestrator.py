from app.core.graph import build_graph
from app.core.llm import get_llm

llm = get_llm()
graph = build_graph()


# 🔥 Auto Title
def generate_title(user_input):
    prompt = f"""
    Generate a short chat title (max 4 words)

    Rules:
    - Only title
    - No punctuation

    Input: {user_input}
    """

    title = llm.invoke(prompt).content.strip()
    return title.replace('"', '').split("\n")[0][:40]


# 🔥 Main System
def multi_agent_system(query, chat_history=None, mode="normal"):

    context = ""

    if chat_history:
        for user, bot in chat_history:
            context += f"User: {user}\nAssistant: {bot}\n"

    state = {
        "query": query,
        "context": context,
        "mode": mode
    }

    result = graph.invoke(state) or {}

    return {
        "response": result.get("final", "No response"),
        "agent": result.get("agent_used", "")
    }