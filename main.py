import os
import uuid
from graph.workflow import build_rml_graph
from dotenv import load_dotenv

load_dotenv()

app = build_rml_graph()

# Updated initial_state to match your new AgentState requirements
initial_state = {
    "csv_path": os.getenv("INPUT_CSV_PATH"),
    "ontology_path": os.getenv("INPUT_ONTOLOGY_PATH"),
    "base_uri": os.getenv("BASE_URI", "http://example.org/"),
    "schema_info": {},
    "ontology_info": {},
    "mapping_plan": {},
    "yarrrml_output": "",  # Match the key used in your nodes
    "feedback": "",  # Initialize for the loop
    "retry_count": 0,  # Initialize for the loop
    "messages": ["System: Starting YARRRML Generation Pipeline"]
}

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

print("--- Running Agentic Pipeline ---")
result = app.invoke(initial_state, config)

# Extract output - Ensure this key matches exactly what nodes.py returns
yarrrml_content = result.get("yarrrml_output", "")

if yarrrml_content:
    # Ensure the directory exists before saving
    os.makedirs("data/output", exist_ok=True)

    output_filename = f"data/output/mapping_{uuid.uuid4().hex[:8]}.yaml"
    with open(output_filename, "w") as f:
        f.write(yarrrml_content)

    print("-" * 30)
    print(f"Success! YARRRML saved to: {output_filename}")
    print(f"Total attempts made: {result.get('retry_count')}")
    print("-" * 30)
else:
    print("Error: No YARRRML was generated. Check agent feedback in the logs.")


# if yarrrml_content:
#     output_filename = "data/output/mapping.yaml"
#     with open(output_filename, "w") as f:
#         f.write(yarrrml_content)
#     print(f"Success! YARRRML saved to {output_filename}")
# else:
#     print("Error: No YARRRML was generated. Check the agent logs.")