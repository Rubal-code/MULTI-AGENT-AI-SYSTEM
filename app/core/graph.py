from langgraph.graph import StateGraph, END
from typing import TypedDict

from app.agents.research_agent import research_agent
from app.agents.planner_agent import planner_agent
from app.agents.summarizer_agent import summarizer_agent


# ================= STATE ================= #
class AgentState(TypedDict):
    query: str
    context: str
    research: str
    final: str
    mode: str
    agent_used: str


# ================= NODES ================= #

# 🔍 Research Node
def research_node(state: AgentState):

    full_query = state.get("context", "") + "\nUser: " + state["query"]

    result = research_agent(full_query)

    return {
        **state,
        "research": result.content,
        "agent_used": "research_agent"
    }


# 🧠 Planner Node
def planner_node(state: AgentState):
    result = planner_agent(state["research"])

    return {
        **state,
        "final": result.content,
        "agent_used": state.get("agent_used", "") + " -> planner_agent"
    }


# ✂️ Summarizer Node
def summarizer_node(state: AgentState):

    mode = state.get("mode", "short")
    style = "brief" if mode == "short" else "detailed"

    result = summarizer_agent(state["research"], style)

    return {
        **state,
        "final": result.content,
        "agent_used": state.get("agent_used", "") + " -> summarizer_agent"
    }


# 🧠 Router (FIXED)
def router(state: AgentState):

    query = state["query"].lower()
    mode = state.get("mode", "normal")

    if "plan" in query or "roadmap" in query:
        return "planner"

    elif mode == "short" or "brief" in query:
        return "summarizer"

    else:
        return "final"


# 🎯 Final Node
def final_node(state: AgentState):

    # Keep existing output if present
    if state.get("final"):
        final_output = state["final"]
    else:
        final_output = state.get("research", "")

    mode = state.get("mode", "normal")

    if mode == "short":
        final_output = final_output[:200]

    return {
        **state,
        "final": final_output,
        "agent_used": state.get("agent_used", "") + " -> final"
    }


# ================= BUILD GRAPH ================= #

def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("research", research_node)
    builder.add_node("planner", planner_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("final", final_node)

    builder.set_entry_point("research")

    builder.add_conditional_edges(
        "research",
        router,
        {
            "planner": "planner",
            "summarizer": "summarizer",
            "final": "final"
        }
    )

    builder.add_edge("planner", "final")
    builder.add_edge("summarizer", "final")
    builder.add_edge("final", END)

    return builder.compile()