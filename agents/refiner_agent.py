from config.settings import get_llm
from data.checkpoints import AgentState

def call_refiner_llm(state: AgentState):
    llm = get_llm()

    # Extracting ontology for better logic checking
    ontology = state.get("ontology_info", {}).get("raw", "No ontology provided.")
    is_syntax_error = "SYNTAX_ERROR" in state.get("feedback", "")

    prompt = f"""
    You are a Knowledge Graph Quality Assurance expert.

    ONTOLOGY CONTEXT:
    {ontology}

    CURRENT YARRRML:
    {state['yarrrml_output']}

    VALIDATION FEEDBACK:
    {state['feedback']}

    YOUR TASK:
    {"Fix the syntax error identified by the compiler above." if is_syntax_error else "Verify URI logic and semantic correctness."}

    CRITICAL LOGIC CHECK:
    - Subject (s:) templates must match Object (o:) templates in joins to ensure connectivity.
    - Ensure all prefixes used are defined in the 'prefixes' section.
    - Check if the classes and properties match the provided ONTOLOGY CONTEXT.

    If it is perfect, return 'APPROVED'. 
    If not, provide a specific report on what to fix.
    """

    response = llm.invoke(prompt)
    return response.content