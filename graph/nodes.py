from tools.rml_tools import get_csv_schema, get_ontology_subgraph
from agents.schema_agent import call_schema_llm
from agents.mapper_agent import call_mapper_llm
from agents.yarrrml_agent import call_yarrrml_architect_llm
from data.checkpoints import AgentState
from agents.refiner_agent import call_refiner_llm

import yatter
from ruamel.yaml import YAML
import io


def schema_agent_node(state):
    # 1. Physical extraction (The Tool)
    raw_schema = get_csv_schema(state["csv_path"])

    # 2. Semantic understanding (The Agent)
    analysis = call_schema_llm(raw_schema)

    # 3. Update State
    return {
        "schema_info": {
            "raw": raw_schema,
            "analysis": analysis
        },
        "messages": [f"Schema Agent: Identified data as {analysis[:50]}..."]
    }


def ontology_scout_node(state):
    keywords = state["schema_info"]["raw"]["columns"]
    ontology_info = get_ontology_subgraph(state["ontology_path"], keywords)
    return {
        "ontology_info": {"raw": ontology_info},
        "messages": ["Ontology Scout: Extracted relevant ontology subgraph"]
    }


def mapper_agent_node(state):
    mapping = call_mapper_llm(
        state["schema_info"],
        state["ontology_info"]
    )
    return {
        "mapping_plan": {"analysis": mapping},
        "messages": [f"Mapper Agent: {mapping[:50]}..."]
    }


def yarrrml_architect_node(state):
    # Get current retries or default to 0
    current_retries = state.get("retry_count", 0)

    yarrrml = call_yarrrml_architect_llm(state)

    return {
        "yarrrml_output": yarrrml,
        "retry_count": current_retries + 1,  # Increment the counter
        "messages": [f"YARRRML Architect: Generated attempt #{current_retries + 1}"]
    }


def validation_node(state: AgentState):
    yarrrml_content = state["yarrrml_output"]
    yaml = YAML(typ='safe', pure=True)

    try:
        # Load the string as YAML and attempt Yatter translation
        yarrrml_data = yaml.load(yarrrml_content)
        rml_content = yatter.translate(yarrrml_data)

        # If successful, move to logic check
        return {
            "messages": ["Validator: Syntax is valid."],
            "feedback": "PASSED_SYNTAX"
        }
    except Exception as e:
        # Capture the specific error (e.g., ScannerError, YatterException)
        error_log = str(e)
        return {
            "messages": [f"Validator: Syntax Error found: {error_log[:100]}..."],
            "feedback": f"SYNTAX_ERROR: {error_log}",
            "retry_needed": True
        }


def refiner_agent_node(state):
    # # Only runs if syntax is already PASSED_SYNTAX
    # yarrrml = state["yarrrml_output"]
    # ontology = state["ontology_info"]

    # We call a specialized prompt to check for URI/Join logic
    logic_feedback = call_refiner_llm(state)

    if "APPROVED" in logic_feedback:
        return {
            "feedback": "APPROVED",
            "messages": ["Refiner: Logic check passed. URIs are consistent."]
        }
    else:
        return {
            "feedback": f"LOGIC_ERROR: {logic_feedback}",
            "messages": ["Refiner: Found logic/URI issues."]
        }