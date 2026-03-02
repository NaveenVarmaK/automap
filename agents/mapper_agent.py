from config.settings import get_llm

def call_mapper_llm(schema, ontology):
    llm = get_llm()
    prompt = f"""
    Compare this CSV Schema: {schema}
    With this Ontology: {ontology}
    Suggest which CSV columns map to which Ontology Classes/Properties.
    Return only the mapping logic.
    """
    response = llm.invoke(prompt)
    return response.content