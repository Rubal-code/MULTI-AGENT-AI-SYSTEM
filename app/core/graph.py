from langgraph.graph import StateGraph, END
from typing import TypedDict

#  Proper state definition
class AgentState(TypedDict):
    query: str
    result: str

#  Node
def test_node(state: AgentState):
    return {
        "query": state["query"],
        "result": "graph is working 🚀"
    }

#  Build graph
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("test", test_node)

    builder.set_entry_point("test")

    builder.add_edge("test", END)

    return builder.compile()