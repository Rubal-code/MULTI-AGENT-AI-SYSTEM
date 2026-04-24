from langgraph.graph import StateGraph, END
from typing import TypedDict

from app.agents.research_agent import research_agent
from app.agents.planner_agent import planner_agent
from app.agents.summarizer_agent import summarizer_agent
from app.core.llm import get_llm

llm = get_llm()


# ================= STATE ================= #
class AgentState(TypedDict):
    query: str
    context: str
    research: str
    final: str
    mode: str
    agent_used: str


# ================= NODES ================= #

def research_node(state: AgentState):
    full_query = state.get("context", "") + "\nUser: " + state["query"]
    result = research_agent(full_query)

    return {
        **state,
        "research": result.content,
        "agent_used": "research_agent"
    }


def planner_node(state: AgentState):
    result = planner_agent(state["research"])

    return {
        **state,
        "final": result.content,
        "agent_used": state.get("agent_used", "") + " -> planner_agent"
    }


def summarizer_node(state: AgentState):
    mode = state.get("mode", "short")
    style = "brief" if mode == "short" else "detailed"

    result = summarizer_agent(state["research"], style)

    return {
        **state,
        "final": result.content,
        "agent_used": state.get("agent_used", "") + " -> summarizer_agent"
    }


# 🔥 Parallel (FIXED)
def parallel_node(state: AgentState):

    summary = summarizer_agent(state["research"], "detailed")
    plan = planner_agent(state["research"])

    combined = f"""
📘 **Concept Explanation**
{summary.content}

---

🧠 **Complete Roadmap**
{plan.content}
"""

    return {
        **state,
        "final": combined,
        "agent_used": state.get("agent_used", "") + " -> summarizer + planner"
    }


# 🔥 SMART ROUTER
def llm_router(state: AgentState):

    query = state["query"]

    prompt = f"""
    Classify the user query:

    planner → roadmap, steps, learning plan
    summarizer → short/brief/simple explanation
    parallel → full explanation + roadmap
    final → normal explanation

    RULE:
    - Output only ONE word

    Query:
    {query}
    """

    decision = llm.invoke(prompt).content.strip().lower()

    if "planner" in decision:
        return "planner"
    elif "summarizer" in decision:
        return "summarizer"
    elif "parallel" in decision:
        return "parallel"
    else:
        return "final"


#  FINAL NODE (NO TRUNCATION BUG)
def final_node(state: AgentState):

    final_output = state.get("final", state.get("research", ""))

    mode = state.get("mode", "normal")

    #  DO NOT CUT roadmap outputs
    if mode == "short" and state.get("research"):
        summary = summarizer_agent(state["research"], "brief").content
    
        # limit words instead of characters
        words = summary.split()
        final_output = " ".join(words[:40])

    return {
        **state,
        "final": final_output,
        "agent_used": state.get("agent_used", "") + " -> final"
    }


# ================= BUILD ================= #

def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("research", research_node)
    builder.add_node("planner", planner_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("parallel", parallel_node)
    builder.add_node("final", final_node)

    builder.set_entry_point("research")

    builder.add_conditional_edges(
        "research",
        llm_router,
        {
            "planner": "planner",
            "summarizer": "summarizer",
            "parallel": "parallel",
            "final": "final"
        }
    )

    builder.add_edge("planner", "final")
    builder.add_edge("summarizer", "final")
    builder.add_edge("parallel", "final")
    builder.add_edge("final", END)

    return builder.compile()