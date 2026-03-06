# Automap 

**Agentic Knowledge Graph Generation**

**Project Status: Under Development** This project is currently in an active development phase.

## Overview

**Automap** is a agentic pipeline that leverages Large Language Models (LLMs) and [**LangGraph**](https://www.langchain.com/langgraph) to automate the creation of RML mappings and Knowledge Graph materialization. The system uses a multi-agent architecture to analyze CSV schemas, scout ontologies, and iteratively refine YARRRML mappings before final execution.

### Key Features

* **Multi-Agent Orchestration:** Specialized agents for schema analysis, ontology mapping, and YARRRML architecture.
* **Self-Correction Loop:** Automatic syntax validation and logical refinement of mappings.
* **Terminal-Native Observability:** Real-time streaming of agent states and reasoning directly to the console.
* **Native Docker Support:** Pre-configured environment with automated compatibility patches.

---

## Observability & Debugging

While [**LangGraph**](https://www.langchain.com/langgraph) is open-source, its primary visualization tool, [**LangSmith**](https://docs.langchain.com/oss/python/langgraph/studio), often presents limitations for developers:

* **Tier Constraints:** Free tiers have strict trace limits and data retention periods.
* **Privacy & Latency:** Sending agent traces to a third-party cloud isn't always feasible for sensitive data or high-latency environments.
* **Complexity:** Setup requires API keys and external dashboard management.

### **The "Terminal-First" Approach**

To keep this project lightweight and independent, we use **Native Terminal Streaming**. The pipeline uses a custom event-loop in `main.py` to provide real-time feedback:

* **Live Stage Tracking:** See exactly which node (Architect, Refiner, Validator) is active.
* **Logic Refinement Feedback:** The `Logic Refiner` agent prints its specific reasoning and critique directly to your terminal.
* **Syntax Validation:** Instant "VALID/INVALID" status reports during the YARRRML generation phase.

---

## Installation & Setup

This project uses `uv` for lightning-fast Python dependency management and `docker` for containerized execution.

### 1. Local Environment Setup

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

```bash
# Sync dependencies
uv sync

# Apply essential Morph-KGC compatibility patches
# NOTE: This script is currently optimized for Linux. 
bash scripts/patch_morph_kgc.sh

# Set up your environment variables
cp .env.example .env  # Edit with your LLM API keys and file paths

```

### 2. Execution

Once the environment is set up and patched, run the pipeline with:

```bash
uv run python main.py

```

### 3. Running via Docker (Recommended)

The Dockerfile automatically handles Python 3.12 compatibility patches for `morph-kgc` and is the most reliable way to run the pipeline.

```bash
docker-compose up --build

```

---

## Post-Install Patches (Compatibility Note)

The upstream dependency `morph-kgc` requires specific patches to support Python 3.12, Pandas 2.0+, and Numpy 2.0+.

> [!IMPORTANT]
> **Platform Support:** The `scripts/patch_morph_kgc.sh` script is currently **Linux-only**.
> * **macOS Users:** You may need to install `gnu-sed` or manually adjust the `sed -i` commands in the script.
> * **Windows Users:** Please use the **Docker** installation or manually apply the changes listed below in your site-packages.
> 
> 

| File | Issue | Fix |
| --- | --- | --- |
| `mapping_partitioner.py` | `value_counts()` index access | `.value_counts()[0]` → `.value_counts().iloc[0]` |
| `utils.py` | `np.NaN` alias removal | `np.NaN` → `np.nan` |

---

## Project Structure

* **`agents/`**: Core LLM logic for the Schema, Mapper, Architect, and Refiner agents.
* **`graph/`**: LangGraph definitions (`workflow.py`) and node execution logic (`nodes.py`).
* **`data/`**: Input CSVs/Ontologies and timestamped output run directories.
* **`tools/`**: Contains functions to extract small part of the csv and relevant ontology from the given input.
* **`scripts/`**: Critical patch scripts for upstream dependency fixes.

---

## Research & Citations

If you use this tool in an academic context, please cite:

**Morph-KGC**

* Arenas-Guerrero, J., et al. (2024). *An RML-FNML module for Python user-defined functions in Morph-KGC*. SoftwareX.
* Arenas-Guerrero, J., et al. (2024). *Morph-KGC: Scalable knowledge graph materialization with mapping partitions*. Semantic Web.

**Yatter**

* Iglesias-Molina, A., et al. (2023). *Human-Friendly RDF Graph Construction: Which One Do You Chose?*. ICWE.

---

## Acknowledgments

### Funding

This work has received funding from the **PIONERA** project (*Enhancing interoperability in data spaces through artificial intelligence*), a project funded in the context of the call for Technological Products and Services for Data Spaces of the **Ministry for Digital Transformation and Public Administration** within the framework of the **PRTR** funded by the **European Union (NextGenerationEU)**.

<img width="1961" height="169" alt="image" src="https://github.com/user-attachments/assets/941a0db1-547f-48d0-b627-904098d607c9" />

## Contributors

**Naveen Varma KALIDINDI** - naveen.kalidindi@upm.es

*Universidad Politécnica de Madrid (UPM)*

