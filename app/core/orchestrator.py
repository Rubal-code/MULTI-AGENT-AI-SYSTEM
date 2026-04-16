from app.core.graph import build_graph
from app.core.llm import get_llm

# Initialize
llm = get_llm()
graph = build_graph()


# 🔥 Auto Title Generator
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


# 🔥 MAIN SYSTEM
def multi_agent_system(query, chat_history=None, mode="normal"):

    # 🧠 Build memory context
    context = ""

    if chat_history:
        for user, bot in chat_history:
            context += f"User: {user}\nAssistant: {bot}\n"

    # ✅ Separate query & context (FIXED)
    state = {
        "query": query,
        "context": context,
        "mode": mode
    }

    # 🚀 Run graph
    result = graph.invoke(state) or {}

    return {
        "response": result.get("final", "No response generated"),
        "agent": result.get("agent_used", "")
    }