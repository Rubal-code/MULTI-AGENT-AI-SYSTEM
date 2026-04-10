from app.agents.research_agent import research_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.planner_agent import planner_agent

def multi_agent_system(query):
    research = research_agent(query)
    
    summary = summarizer_agent(research.content)
    
    plan = planner_agent(summary.content)
    
    return {
        "research": research.content,
        "summary": summary.content,
        "plan": plan.content
    }