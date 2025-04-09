import requests
import json
import datetime
import time
from config.config import AZURE_OPENAI_ENDPOINT, API_KEY, MAX_TOKENS, TEMPERATURE, MAX_RELEVANT_FACTS

KG_FILE = "knowledge_graph/sliced/kg_sliced.json"
QA_DATASET_FILE = "qa_Dataset/qa_data.json"
LOG_FILE = "results/results.json"

def load_kg(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def filter_kg_facts(kg_data, question):
    stopwords = {"what", "is", "the", "of", "a", "an", "which", "in", "on", "and", "or", "?"}
    question_tokens = [w for w in question.lower().split() if w not in stopwords]
    filtered = []
    for item in kg_data:
        label = item.get("label_en", "").lower()
        desc = item.get("description_en", "").lower()
        if any(token in label or token in desc for token in question_tokens):
            fact = {
                "subject": item.get("label_en", ""),
                "relation": item.get("id", ""),
                "object": item.get("description_en", "")
            }
            filtered.append(fact)
            if len(filtered) >= MAX_RELEVANT_FACTS:
                break
    return filtered

def build_system_prompt(facts):
    if not facts:
        facts_str = "No relevant facts found in the knowledge graph."
    else:
        facts_str = "\n".join(f"{f['subject']} - {f['relation']} - {f['object']}" for f in facts)
    system_prompt = (
        "You are a helpful AI that uses the provided knowledge to explain answers.\n\n"
        "Background knowledge:\n"
        f"{facts_str}\n\n"
        "If the provided knowledge is insufficient, say so.\n"
    )
    return system_prompt

def call_azure_openai(payload, headers, max_retries=3, wait_seconds=60):
    for attempt in range(max_retries):
        response = requests.post(AZURE_OPENAI_ENDPOINT, json=payload, headers=headers)
        if response.status_code == 429:
            print(f"Rate Limit (429) erreicht, warte {wait_seconds} Sekunden... (Versuch {attempt+1}/{max_retries})")
            time.sleep(wait_seconds)
        else:
            return response
    return response

def ask_llm_only(question):
    system_prompt = (
        "You are a helpful AI that answers questions to the best of your ability. "
        "You have no additional context beyond the user's question. "
        "If you are unsure, say so."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    response = call_azure_openai(payload, headers)
    if response.status_code == 200:
        resp_json = response.json()
        try:
            return resp_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return f"Unexpected response format: {resp_json}"
    else:
        return f"Error {response.status_code}: {response.text}"

def ask_llm_with_kg(question, kg_data):
    relevant_facts = filter_kg_facts(kg_data, question)
    system_msg = build_system_prompt(relevant_facts)
    payload = {
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    response = call_azure_openai(payload, headers)
    if response.status_code == 200:
        resp_json = response.json()
        try:
            llm_answer = resp_json["choices"][0]["message"]["content"]
            return llm_answer, relevant_facts
        except (KeyError, IndexError):
            return f"Unexpected response format: {resp_json}", relevant_facts
    else:
        return f"Error {response.status_code}: {response.text}", relevant_facts

def log_answers(item, llm_answer, kg_answer, used_facts, log_file=LOG_FILE):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "question": item["question"],
        "reference_knowledge_snippet": item.get("knowledge_snippet", ""),
        "reference_answer": item.get("answer", ""),
        "reference_explanation": item.get("explanation", ""),
        "llm_answer_only": llm_answer,
        "llm_answer_with_kg": kg_answer,
        "used_facts": used_facts
    }
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print("Lade großes KG, bitte warten...")
    kg_data = load_kg(KG_FILE)
    print(f"KG geladen: {len(kg_data)} Einträge.")
    with open(QA_DATASET_FILE, "r", encoding="utf-8") as f:
        qa_dataset = json.load(f)["qa_dataset"]
    for i, item in enumerate(qa_dataset, start=1):
        question = item["question"]
        print(f"\n=== {i}/{len(qa_dataset)}: Frage: {question} ===")
        llm_only_answer = ask_llm_only(question)
        print(" - LLM-Only:", llm_only_answer)
        llm_kg_answer, used_facts = ask_llm_with_kg(question, kg_data)
        if isinstance(used_facts, list):
            print(f" - LLM+KG: {llm_kg_answer} (Fakten: {len(used_facts)})")
        else:
            print(f" - LLM+KG: {llm_kg_answer}")
        log_answers(item, llm_only_answer, llm_kg_answer, used_facts, LOG_FILE)
        print(f"Ergebnis in '{LOG_FILE}' protokolliert.")
    print("\nFertig! Alle Fragen wurden bearbeitet.")
