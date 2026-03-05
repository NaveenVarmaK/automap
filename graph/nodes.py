from tools.rml_tools import get_csv_schema, get_ontology_subgraph
from agents.schema_agent import call_schema_llm
from agents.mapper_agent import call_mapper_llm
from agents.yarrrml_agent import call_yarrrml_architect_llm
from data.checkpoints import AgentState
from agents.refiner_agent import call_refiner_llm
from datetime import datetime

import yatter
from ruamel.yaml import YAML
import io
import os

import morph_kgc


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
    current_retries = state.get("retry_count", 0)
    yarrrml = call_yarrrml_architect_llm(state)

    # ANTI-HALLUCINATION CLEANUP:
    # Remove the "~iri" the LLM likes to add incorrectly
    yarrrml = yarrrml.replace("~iri", "")

    # Save for debug
    os.makedirs("data/output/debug", exist_ok=True)
    with open("data/output/debug/last_attempt.yaml", "w") as f:
        f.write(yarrrml)

    return {
        "yarrrml_output": yarrrml,
        "retry_count": current_retries + 1,
        "feedback": "",
        "messages": [f"Architect: Generated attempt #{current_retries + 1}"]
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



def _internal_yarrrml_to_rml(yarrrml_content, csv_path):
    """
    Helper to convert YARRRML string to RML string and patch CSV paths.
    """
    yaml = YAML(typ='safe')
    yarrrml_data = yaml.load(yarrrml_content)

    # Translate YARRRML to RML (Turtle syntax)
    rml_content = yatter.translate(yarrrml_data)

    # Patch the rml:source to use the absolute path of the CSV
    csv_filename = os.path.basename(csv_path)
    abs_csv_path = os.path.abspath(csv_path)

    # Replace the relative filename with the absolute path for Morph-KGC
    patched_rml = rml_content.replace(
        f'rml:source "{csv_filename}"',
        f'rml:source "{abs_csv_path}"'
    )
    return patched_rml


def kg_generation_node(state):
    """
    Converts the approved YARRRML to RML and runs Morph-KGC.
    Outputs to a dedicated run directory.
    """
    yarrrml_content = state.get("yarrrml_output")
    csv_path = state.get("csv_path")

    # Use the run_dir defined in the state, or fallback to a timestamped one
    run_dir = state.get("run_dir", f"data/output/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(run_dir, exist_ok=True)

    output_path = os.path.abspath(os.path.join(run_dir, "knowledge_graph.nt"))

    try:
        print(f"[System] Converting YARRRML to RML in {run_dir}...")
        rml_content = _internal_yarrrml_to_rml(yarrrml_content, csv_path)

        # Save RML temporarily inside the run directory
        rml_tmp_path = os.path.join(run_dir, "temp_mapping.ttl")
        with open(rml_tmp_path, "w") as f:
            f.write(rml_content)

        config_str = f"""
[CONFIGURATION]
output_file: {output_path}
output_format: N-TRIPLES

[DataSource1]
mappings: {rml_tmp_path}
        """

        print("[System] Materializing Knowledge Graph...")
        g_rdf = morph_kgc.materialize(config_str)

        if not os.path.exists(output_path):
            from rdflib import Graph, ConjunctiveGraph
            if isinstance(g_rdf, (Graph, ConjunctiveGraph)):
                g_rdf.serialize(destination=output_path, format="ntriples")

        return {
            "rdf_output": output_path,
            "messages": [f"KG Generation: Success! Created in {run_dir}"]
        }

    except Exception as e:
        error_msg = f"KG Generation Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {"messages": [error_msg]}