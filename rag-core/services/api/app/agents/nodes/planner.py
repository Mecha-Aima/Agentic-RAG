import json
import logging
from services.api.app.agents.state import AgentState
from services.api.app.clients.ray_llm import llm_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a RAG Planning Agent.
Analyze the User Query and Conversation History.

Primary domain: Kubernetes documentation.
Default behavior: prefer "retrieve" for Kubernetes questions.

Decide the next step:
1. If the user greets (Hello/Hi), output "direct_answer".
2. If the question is about Kubernetes concepts, APIs, behavior, troubleshooting, or best practices, output "retrieve".
3. Use "tool_use" only when retrieval is not the best fit (for example: explicit math evaluation, explicit graph relation lookup, explicit vector lookup, or explicit web lookup).
4. If you choose "tool_use", pick one tool:
   - calculator: evaluate math expressions.
   - graph_search: search knowledge graph relations/entities.
   - vector_search: search vector database passages.
   - web_search: search public web for recent/external information.

Output JSON format ONLY:
{
    "action": "retrieve" | "direct_answer" | "tool_use",
    "refined_query": "The standalone search query",
    "tool_choice": "calculator" | "graph_search" | "vector_search" | "web_search" | "",
    "tool_input": "input string for selected tool, empty when not tool_use",
    "reasoning": "Why you chose this action"
}
"""

async def planner_node(state: AgentState) -> dict:
    """
    Decides the path through the LangGraph.
    """
    logger.info("Planner Node: Analyzing query...")
    
    # Extract latest user message
    # state['messages'] is a list of dicts or objects
    last_message = state["messages"][-1]
    user_query = last_message.content if hasattr(last_message, 'content') else last_message['content']

    # Call LLM to plan
    try:
        response_text = await llm_client.chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0 # Deterministic planning
        )
        
        # Parse JSON
        plan = json.loads(response_text)
        
        logger.info(f"Plan derived: {plan['action']}")

        action = plan.get("action", "retrieve")
        tool_choice = (plan.get("tool_choice") or "").strip()
        tool_input = (plan.get("tool_input") or "").strip()

        if action != "tool_use":
            tool_choice = ""
            tool_input = ""

        if action == "tool_use" and not tool_input:
            tool_input = plan.get("refined_query", user_query)

        # Update State
        return {
            "current_query": plan.get("refined_query", user_query),
            "plan": [plan.get("reasoning", "Planning completed.")],
            "tool_choice": tool_choice,
            "tool_input": tool_input,
        }
        
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        # Fallback: Assume we need to search
        return {
            "current_query": user_query,
            "plan": ["Error in planning, defaulting to retrieval."],
            "tool_choice": "",
            "tool_input": "",
        }