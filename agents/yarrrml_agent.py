from config.settings import get_llm
import os
from dotenv import load_dotenv

load_dotenv()


def call_yarrrml_architect_llm(state: dict):
    llm = get_llm()
    csv_name = os.path.basename(state["csv_path"])
    base_uri = state.get("base_uri", "http://example.org/")
    mapping = state["mapping_plan"].get("analysis", "")
    ontology = state["ontology_info"].get("raw", "")

    feedback = state.get("feedback", "")
    feedback_section = ""

    # If we have a syntax error, emphasize it in the prompt
    if feedback and "PASSED" not in feedback and "APPROVED" not in feedback:
        feedback_section = f"""
        ### CRITICAL: FIX PREVIOUS SYNTAX ERRORS
        Your last output was invalid. 
        ERROR LOG: {feedback}

        Instructions for fix:
        1. Check for missing colons or incorrect indentation.
        2. Ensure all referenced $(columns) exist in the CSV schema.
        3. Do not include any explanation text.
        """

    prompt = f"""Generate a valid YARRRML mapping file based on the provided ontology and mapping plan.
        {feedback_section}

        Target CSV: {csv_name}
        Base URI: {base_uri}
        Ontology Context: {ontology}
        Mapping Plan: {mapping}

        ### STRUCTURAL REQUIREMENTS (Apply to any domain):
        1. SCHEMA COMPLETENESS: Map EVERY column mentioned in the Mapping Plan. Ensure no attributes are dropped.
        2. RELATIONAL INTEGRITY: Identify the primary class (Subject) and ensure it has Predicate-Object properties that link to all secondary classes (Objects) defined in the mapping plan.
        3. URI COHERENCE: For classes originating from the same CSV row, use a consistent unique identifier (ID) in the Subject URI templates to ensure the Knowledge Graph is fully connected.
        4. DATA TYPING: Assign appropriate XSD datatypes (xsd:integer, xsd:float, xsd:boolean, xsd:dateTime) as indicated by the column values and ontology.
        5. URI FORMATTING: Always wrap URI templates in double quotes and append "~iri" to object properties that refer to other mappings.

        Rules:
        - Output ONLY valid YARRRML (YAML).
        - Format Subject URIs as: "{base_uri}resource_name/$(ID_COLUMN)"
        - Ensure all prefixes used in the mappings are defined in the 'prefixes:' section.
        - No markdown code blocks, preamble, or post-text.
        
        ... (other context) ...

        ### STRICT OUTPUT RULES:
        1. NO SYMBOLS IN STRINGS: Never use '~iri' or '~csv' inside the predicate-object (po) lists.
        2. QUOTES: Every single 's:' value and every single value inside the 'po:' lists MUST be wrapped in double quotes.
       - Correct: s: "http://example.com/id/$(instant)"
       - Correct: - ["bikeshare:hasInstant", "$(instant)", "xsd:integer"]
        3. NO SPECIAL FUNCTIONS: Unless specifically asked, do not use 'condition:' or 'function:' logic. Use simple shared URIs to link classes.
        4. ALIGNMENT: Use exactly 2 spaces for indentation. No tabs.
        
        """

    response = llm.invoke(prompt)
    content = response.content.strip()

    # Robust cleanup: Remove markdown fences if the LLM ignored instructions
    if "```" in content:
        # Split by backticks and take the content inside
        parts = content.split("```")
        for part in parts:
            if "prefixes:" in part or "mappings:" in part:
                content = part
                break
        # Remove language identifiers like 'yaml' or 'yml' from the first line
        lines = content.splitlines()
        if lines and (lines[0].strip().lower() in ["yaml", "yml"]):
            content = "\n".join(lines[1:])

    return content.strip()