from config.settings import get_llm


def call_rml_architect_llm(schema_info: dict, mapping_plan: dict, ontology_info: dict):
    llm = get_llm()

    columns = schema_info.get("raw", {}).get("columns", [])
    mapping = mapping_plan.get("analysis", "")
    ontology = ontology_info.get("raw", "")

    # Keep prompt short — only pass mapping and ontology, not full schema analysis
    prompt = f"""Generate a valid RML mapping in Turtle syntax for a CSV file called "bike_data.csv".

Ontology prefixes and properties to use:
{ontology}

Column-to-property mappings:
{mapping}

For columns without ontology mappings, use ex: namespace (e.g., ex:hasSeason, ex:hasHour).
All columns: {columns}

Output ONLY Turtle RML syntax. No explanation. Start with @prefix lines.

@prefix rr: <http://www.w3.org/ns/r2rml#> .
@prefix rml: <http://semweb.mmlab.be/ns/rml#> .
@prefix ql: <http://semweb.mmlab.be/ns/ql#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/bikeshare#> .
"""

    print(f"\n[DEBUG] Prompt length: {len(prompt)} chars")

    response = llm.invoke(prompt)

    print(f"[DEBUG] Response type: {type(response)}")
    print(f"[DEBUG] Response content type: {type(response.content)}")
    print(f"[DEBUG] Response content length: {len(response.content)}")
    print(f"[DEBUG] Full response content:\n{response.content}")

    content = response.content.strip()

    # Strip markdown fences if LLM wraps output
    if content.startswith("```"):
        lines = content.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines).strip()

    return content