from langgraph.graph import StateGraph, END
from data.checkpoints import AgentState
from graph.nodes import schema_agent_node, ontology_scout_node, mapper_agent_node, rml_architect_node

def build_rml_graph():
    workflow = StateGraph(AgentState)

    # Node 1: Analyze Structure
    workflow.add_node("analyze_schema", schema_agent_node)

    # Node 2: Find Ontology Matches
    workflow.add_node("scout_ontology", ontology_scout_node)

    # Node 3: Create Mapping Logic (Reasoning)
    workflow.add_node("map_semantics", mapper_agent_node)

    # Node 4: Generate RML Code
    workflow.add_node("generate_rml", rml_architect_node)

    # Connections
    workflow.set_entry_point("analyze_schema")
    workflow.add_edge("analyze_schema", "scout_ontology")
    workflow.add_edge("scout_ontology", "map_semantics")
    workflow.add_edge("map_semantics", "generate_rml")
    workflow.add_edge("generate_rml", END)

    # Memory Checkpoint (SQLite is easiest for local dev)
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)

from agents.mapper_agent import call_mapper_llm

def mapper_agent_node(state):
    mapping = call_mapper_llm(
        state["schema_info"],
        state["ontology_info"]
    )
    return {
        "mapping_plan": {"analysis": mapping},
        "messages": [f"Mapper Agent: {mapping[:50]}..."]
    }