from langgraph.graph import StateGraph, END
from services.api.app.agents.state import AgentState
from services.api.app.agents.nodes.retriever import retrieve_node
from services.api.app.agents.nodes.responder import generate_node
from services.api.app.agents.nodes.planner import planner_node
from services.api.app.agents.nodes.tool import tool_node

# Initialize the Graph
workflow = StateGraph(AgentState)

# 1. Define Nodes (The Logic Steps)
# These functions (imported above) will be implemented in the 'nodes/' folder next
workflow.add_node("planner", planner_node)       # Rewrites query / Decides steps
workflow.add_node("tool", tool_node)
workflow.add_node("retriever", retrieve_node)    # Hits Qdrant & Neo4j
workflow.add_node("responder", generate_node)    # Calls Ray Serve LLM


def route_after_planner(state: AgentState) -> str:
	tool_choice = (state.get("tool_choice") or "").strip()
	if tool_choice:
		return "tool"
	return "retriever"

# 2. Define Edges (The Flow)
# Start -> Plan -> Retrieve -> Generate -> End
workflow.set_entry_point("planner")

workflow.add_conditional_edges(
	"planner",
	route_after_planner,
	{
		"tool": "tool",
		"retriever": "retriever",
	},
)
workflow.add_edge("tool", "responder")
workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END) # In a more complex agent, we could loop back if answer is bad

# 3. Compile the Graph
# This creates the runnable application
agent_app = workflow.compile()