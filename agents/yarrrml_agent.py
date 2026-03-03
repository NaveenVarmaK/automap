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

    # NEW: Extract feedback from state
    feedback = state.get("feedback", "")
    feedback_section = ""
    if feedback and "PASSED" not in feedback and "APPROVED" not in feedback:
        feedback_section = f"""
        ### PREVIOUS ATTEMPT FAILED
        The previous YARRRML you generated had errors. 
        FEEDBACK FROM VALIDATOR: {feedback}
        Please correct these errors in your new response.
        """

    prompt = f"""Generate a YARRRML mapping file.
    {feedback_section}

    Target CSV: {csv_name}
    Base URI: {base_uri}
    Ontology Context: {ontology}
    Mapping Logic: {mapping}

    Return ONLY valid YARRRML syntax. No talk, no markdown fences.
    """

    response = llm.invoke(prompt)
    return response.content.strip().replace("```yaml", "").replace("```", "")