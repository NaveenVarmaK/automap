from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    csv_path: str
    ontology_path: str
    schema_info: dict
    ontology_info: dict
    mapping_plan: dict
    rml_output: str
    rdf_output: str
    messages: Annotated[List[str], operator.add]