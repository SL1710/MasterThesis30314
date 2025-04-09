# Python project related to the Master Thesis: Optimizing explainability in LLMs through knowledge-augmented prompts without model fine-tuning.

by Simon Langer

## Project Description
This repository contains the code and data from a master's thesis investigating how integrating external Knowledge Graph (KG) facts into Large Language Model prompts can improve explainability and reduce biases without fine-tuning. It demonstrates a lightweight, API-based approach that augments GPT-4 queries with relevant Wikidata facts and evaluates the effects on accuracy, hallucinations, and fairness.

1. **Extraction and Filtering of Wikidata**  
   - `knowledge_graph/kg_slicer.py` reads a compressed Wikidata dump (`.bz2`) and filters it.  
   - The result is a smaller subset stored in `knowledge_graph/sliced/kg_sliced.json`.  
   - **Important:** Because the compressed raw Knowledge Graph is over 80GB and the sliced JSON can exceed 2GB, these files are **not** stored in the repository.

2. **Creating a Q&A Dataset**  
   - `qa_Dataset/qa_generator.py` generates a Q&A dataset from the filtered Wikidata subset.  
   - The result is in `qa_Dataset/qa_data.json`.

3. **Main Program**  
   - `main.py` loads the Knowledge Graph subset (`kg_sliced.json`) and the Q&A dataset (`qa_data.json`) and queries a Large Language Model (LLM).  
   - Two approaches are compared:  
     - **LLM‐Only**: The question is sent to the LLM without any additional context.  
     - **LLM+KG**: The question is sent to the LLM along with relevant facts from the Knowledge Graph.  
   - The results are logged to `results/Results.json`.

4. **Evaluation**  
   - `evaluation/explainability.py` applies local explanation methods (LIME and SHAP) to the Q&A results and stores the outputs in `evaluation/results/explainability.json`.  
   - `evaluation/performance.py` calculates various metrics (accuracy, hallucinations, bias) and writes the results to `evaluation/results/performance.json`.

## Repository Structure
```
.
├── config/
│ └── config.py
├── knowledge_graph/
│ ├── raw/
│ │ └── latest-all.json.bz2
│ ├── sliced/
│ │ └── kg_sliced.json
│ └── kg_slicer.py
├── Evaluation/
│ ├── explainability.py
│ ├── performance.py
│ └── results/
│ ├── explainability.json
│ └── performance.json
├── Qa_Dataset/
│ ├── qa_data.json
│ └── qa_generator.py
├── Results/
│ └── Results.json
├── main.py
└── requirements.txt
```
`config/config.py`
Contains global configurations such as AZURE_OPENAI_ENDPOINT, API_KEY, and parameters like MAX_TOKENS.

`knowledge_graph/kg_slicer.py`
Reads and filters Wikidata data to produce a subset in JSON format.

`qa_Dataset/qa_generator.py`
Uses the filtered Knowledge Graph data to generate a Q&A dataset.

`main.py`
Runs the Q&A experiment and saves answers and metadata in results/Results.json.

`evaluation/explainability.py`
Uses LIME and SHAP for local explanations of the LLM answers. LIME depends on scikit-learn.

`evaluation/performance.py`
Calculates metrics such as accuracy, hallucination rate, and bias rate, saving the output to evaluation/results/performance.json.

## Installation

1. **Clone the repository**  
   ```bash
   git clone <[URL_to_this_repository](https://github.com/SL1710/MasterThesis30314/)>
   cd MasterThesis30314

2. **Create a Python virtual environment (optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/Mac
   # or
   venv\Scripts\activate          # Windows

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

## Usage
1. **Edit Config**<br>
   Add your personal AZURE_OPENAI_ENDPOINT and API_KEY in config/config.py.

2. **Download and Slice the Raw Knowledge Graph (optional)** <br>
   You can download the raw Wikidata Knowledge Graph from Wikimedia dumps (https://dumps.wikimedia.org/wikidatawiki/entities/).
   Place the downloaded latest-all.json.bz2 file in knowledge_graph/raw/.
   Because the compressed raw dump is over 80GB, and the resulting kg_sliced.json can exceed 2GB, these files are not included in the repository.
    ```bash
      python knowledge_graph/kg_slicer.py
      ```
   Result: `knowledge_graph/sliced/kg_sliced.json`.

3. **Generate Q&A Dataset (optional)**
    ```bash
      python qa_Dataset/qa_generator.py
      ```
   Result: `qa_Dataset/qa_data.json`.

4. **Main Program**
    ```bash
      python main.py
      ```
   Result: `results/results.json` with logged answers.

5. **Explainability Analysis**
    ```bash
      python evaluation/explainability.py
      ```
   Result: `evaluation/results/explainability.json`.

6. **Performance Evaluation**
    ```bash
      python evaluation/performance.py
      ```
   Result: `evaluation/results/performance.json`.

      


