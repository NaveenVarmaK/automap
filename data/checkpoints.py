from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    csv_path: str
    ontology_path: str
    base_uri: str
    schema_info: dict
    ontology_info: dict
    mapping_plan: dict
    yarrrml_output: str
    feedback: str
    retry_count: int
    messages: Annotated[List[str], operator.add]