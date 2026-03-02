import os
import uuid
from graph.workflow import build_rml_graph
from dotenv import load_dotenv

load_dotenv()


app = build_rml_graph()

initial_state = {
    "csv_path": os.getenv("INPUT_CSV_PATH"),
    "ontology_path": os.getenv("INPUT_ONTOLOGY_PATH"),
    "schema_info": {},
    "ontology_info": {},
    "mapping_plan": {},
    "rml_output": "",
    "messages": ["System: Starting RML Generation Pipeline"]
}

# New unique thread_id every run — prevents checkpointer replay
config = {"configurable": {"thread_id": str(uuid.uuid4())}}
result = app.invoke(initial_state, config)