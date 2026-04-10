from app.core.llm import get_llm
llm=get_llm()
def research_agent(query):
    prompt=f"Research deeply about : {query}"
    return llm.invoke(prompt)