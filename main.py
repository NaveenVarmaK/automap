import os
import uuid
from graph.workflow import build_rml_graph
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = build_rml_graph()

# Create a unique timestamped directory for this specific run
current_run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_directory = f"data/output/run_{current_run_timestamp}"
os.makedirs(run_directory, exist_ok=True)

initial_state = {
    "csv_path": os.getenv("INPUT_CSV_PATH"),
    "ontology_path": os.getenv("INPUT_ONTOLOGY_PATH"),
    "base_uri": os.getenv("BASE_URI", "http://example.org/"),
    "schema_info": {},
    "ontology_info": {},
    "mapping_plan": {},
    "yarrrml_output": "",
    "rdf_output": "",
    "feedback": "",
    "retry_count": 0,
    "messages": []
}

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

print("\n" + "=" * 50)
print(" STARTING AGENTIC RML PIPELINE")
print("=" * 50 + "\n")

# Use streaming to get real-time terminal notifications
final_state = initial_state
for event in app.stream(initial_state, config):
    for node_name, output in event.items():
        print(f" [STAGE]: {node_name}")

        # Print specific info based on the node
        if "messages" in output:
            print(f"    {output['messages'][-1]}")

        if node_name == "validate_yarrrml":
            status = " VALID" if "PASSED" in output.get("feedback", "") else "❌ INVALID"
            print(f"    Syntax Status: {status}")

        if node_name == "refine_logic":
            # Printing the actual logic error so you can see what the agent is complaining about
            print(f"    🔍 Refiner Feedback: {output.get('feedback', 'No feedback')}")
            status = " APPROVED" if output.get("feedback") == "APPROVED" else " NEEDS FIX"
            print(f"    Logic Review: {status}")

print("\n" + "=" * 50)
print(" PIPELINE COMPLETE")
print("=" * 50)

# The stream iterator doesn't return the full final state easily,
# so we invoke one last time or use the checkpointer to get results.
result = app.get_state(config).values

# ... Your file saving logic ...
if result.get("rdf_output"):
    print(f" Success! Knowledge Graph: {result['rdf_output']}")
else:
    print("❌ Failure: Knowledge Graph was not generated.")

# 1. Handle YARRRML Output
yarrrml_content = result.get("yarrrml_output", "")
if yarrrml_content:
    mapping_filename = os.path.join(run_directory, "final_mapping.yaml")
    with open(mapping_filename, "w") as f:
        f.write(yarrrml_content)
    print(f" Mapping saved to: {mapping_filename}")

if result.get("rdf_output"):
    print(f" Knowledge Graph generated at: {result['rdf_output']}")

# 2. Handle Final RDF Output (The Knowledge Graph)
rdf_path = result.get("rdf_output", "") #
if rdf_path and os.path.exists(rdf_path):
    print(f"Knowledge Graph generated at: {rdf_path}")
else:
    print("Knowledge Graph was not generated. Check agent feedback.")

print("-" * 30)
print(f"Total loop attempts: {result.get('retry_count', 0)}")
print("-" * 30)