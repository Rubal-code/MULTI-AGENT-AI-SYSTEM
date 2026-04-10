from app.core.llm import get_llm

llm = get_llm()

def planner_agent(text):
    prompt = f"Create a structured study plan from:\n{text}"
    return llm.invoke(prompt)