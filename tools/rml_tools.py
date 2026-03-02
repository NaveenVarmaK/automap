import pandas as pd
from rdflib import Graph

def get_csv_schema(path: str):
    """Tool to get headers and a 3-row sample for semantic context."""
    df = pd.read_csv(path, nrows=3)
    return {
        "columns": df.columns.tolist(),
        "sample": df.to_dict(orient='records')
    }


def get_ontology_subgraph(path: str, keywords: list):
    g = Graph()
    g.parse(path)

    relevant_triples = []
    keywords_lower = [k.lower() for k in keywords]

    for s, p, o in g:
        triple_str = f"{s} {p} {o}".lower()
        if any(kw in triple_str for kw in keywords_lower):
            relevant_triples.append(f"{s} {p} {o} .")

    # Return as Turtle string, limit to avoid token overflow
    return "\n".join(relevant_triples[:100])