from services.api.app.agents.state import AgentState
from services.api.app.clients.ray_llm import llm_client

async def generate_node(state: AgentState) -> dict:
    """
    Synthesizes the final answer from retrieved context or tool output.
    """
    query = state["current_query"]
    documents = state.get("documents", [])

    tool_output = ""
    if state.get("tool_choice"):
        for message in reversed(state.get("messages", [])):
            content = message.get("content", "") if isinstance(message, dict) else ""
            if isinstance(content, str) and content.startswith("Tool Output:"):
                tool_output = content.replace("Tool Output:", "", 1).strip()
                break

    context_str = "\n\n".join(documents) if documents else ""
    source_label = "tool output" if tool_output else "retrieved context"
    source_content = tool_output if tool_output else context_str

    prompt = f"""
    You are a helpful Enterprise Assistant. Use the provided source to answer the user's question.

    Source Type:
    {source_label}

    Source Content:
    {source_content}

    Question: 
    {query}

    Instructions:
    1. If source type is retrieved context, cite sources using [Source: Filename] when available.
    2. If source type is tool output, answer directly from that output.
    3. If the source does not contain the answer, say you do not have enough information.
    4. Be concise and professional.
    """
    
    # Call LLM
    answer = await llm_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3 # Low creativity, high fidelity
    )
    
    # Return dictionary to update state (add the AI message)
    return {
        "messages": [{"role": "assistant", "content": answer}]
    }