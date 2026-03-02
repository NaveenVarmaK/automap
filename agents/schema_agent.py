from config.settings import get_llm


def call_schema_llm(schema_data: dict):
    llm = get_llm()

    # This prompt tells the LLM to identify the "Subject" of the CSV
    prompt = f"""
    Analyze this CSV structure:
    Columns: {schema_data['columns']}
    Sample Data: {schema_data['sample']}

    Identify the main entity type (e.g., is this about Weather, People, or Sensors?) 
    and provide a brief description of what each column represents.
    """

    response = llm.invoke(prompt)
    return response.content
