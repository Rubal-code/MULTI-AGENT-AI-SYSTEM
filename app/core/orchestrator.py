from app.agents.research_agent import research_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.planner_agent import planner_agent

def multi_agent_system(query,chat_history=None):
    context=""
    if chat_history:
        for user,bot in chat_history:
            context += f"User: {user}\nBot: {bot}\n"
    
    full_query = context + f"User: {query}\n"
    research = research_agent(full_query)
    
    summary = summarizer_agent(research.content, query)
    
    plan = planner_agent(summary.content)
    
    return {
        "research": research.content,
        "summary": summary.content,
        "plan": plan.content
    }