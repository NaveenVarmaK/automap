from langgraph.graph import StateGraph, END
from data.checkpoints import AgentState
from graph.nodes import schema_agent_node, ontology_scout_node, mapper_agent_node, yarrrml_architect_node, validation_node, refiner_agent_node
from langgraph.checkpoint.memory import MemorySaver


def build_rml_graph():
    workflow = StateGraph(AgentState)

    # Node Definitions
    workflow.add_node("analyze_schema", schema_agent_node)
    workflow.add_node("scout_ontology", ontology_scout_node)
    workflow.add_node("map_semantics", mapper_agent_node)
    workflow.add_node("generate_yarrrml", yarrrml_architect_node)  # FIXED: Was pointing to a string "calidate_syntax"
    workflow.add_node("validate_yarrrml", validation_node)  # FIXED: Ensure this node is added
    workflow.add_node("refine_logic", refiner_agent_node)

    def syntax_check_routing(state):
        feedback = state.get("feedback", "")
        retries = state.get("retry_count", 0)

        if "SYNTAX_ERROR" in feedback:
            if retries >= 3:
                print("!!! MAX RETRIES REACHED: Syntax remains broken.")
                return END
            print(f"-> Syntax error detected. Loop {retries + 1}/3. Returning to Architect.")
            return "generate_yarrrml"

        return "refine_logic"

    def logic_check_routing(state):
        feedback = state.get("feedback", "")
        if "LOGIC_ERROR" in feedback:
            print("-> Logic error detected. Returning to Architect for refinement.")
            return "generate_yarrrml"

        print("-> Logic APPROVED. Proceeding to KG generation.")
        return END  # Or "generate_kg" once implemented

    # Entry Point
    workflow.set_entry_point("analyze_schema")

    # Linear Connections
    workflow.add_edge("analyze_schema", "scout_ontology")
    workflow.add_edge("scout_ontology", "map_semantics")
    workflow.add_edge("map_semantics", "generate_yarrrml")
    workflow.add_edge("generate_yarrrml", "validate_yarrrml")

    # --- CONDITIONAL LOGIC (The "Loop") ---

    # 1. After Syntax Validation
    workflow.add_conditional_edges(
        "validate_yarrrml",
        lambda x: "generate_yarrrml" if "SYNTAX_ERROR" in x.get("feedback", "") else "refine_logic"
    )

    # 2. After Logic Refinement
    # This checks if the Refiner approved it or if it needs to go back to the architect
    workflow.add_conditional_edges(
        "refine_logic",
        lambda x: END if "APPROVED" in x.get("feedback", "") else "generate_yarrrml"
    )

    return workflow.compile(checkpointer=MemorySaver())
