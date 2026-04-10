from app.core.llm import get_llm

llm = get_llm()

def summarizer_agent(text):
    prompt = f"Summarize this in simple terms:\n{text}"
    return llm.invoke(prompt)