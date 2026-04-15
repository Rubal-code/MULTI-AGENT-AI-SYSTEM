from langgraph.graph import StateGraph, END
from typing import TypedDict

from app.agents.research_agent import research_agent
from app.agents.planner_agent import planner_agent
from app.agents.summarizer_agent import summarizer_agent


# STATE
class AgentState(TypedDict):
    query: str
    research: str
    final: str
    mode:str


# Research Node
def research_node(state: AgentState):
    result = research_agent(state["query"])
    return {
        **state,
        "research": result.content
    }


# 🧠 Planner Node
def planner_node(state: AgentState):
    result = planner_agent(state["research"])
    return {
        **state,
        "final": result.content
    }


#  Summarizer Node
def summarizer_node(state: AgentState):
    result = summarizer_agent(state["research"], "brief")
    return {
        **state,
        "final": result.content
    }


#  Router (replaces detect_intent)
def router(state: AgentState):
    query = state["query"].lower()

    if "plan" in query or "roadmap" in query:
        return "planner"
    elif "short" in query or "brief" in query:
        return "summarizer"
    else:
        return "final"


#  Final Node
def final_node(state: AgentState):

    mode = state.get("mode", "normal")

    if mode == "short":
        return {
            **state,
            "final": state["research"][:200]  # simple trim
        }

    elif mode == "detailed":
        return {
            **state,
            "final": state["research"]
        }

    else:
        return {
            **state,
            "final": state["research"]
        }

#  BUILD GRAPH
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