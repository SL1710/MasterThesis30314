import os
import json
import requests
from typing import List, Dict, Any
from rapidfuzz import fuzz
from lime.lime_text import LimeTextExplainer
import shap
import numpy as np
from config.config import AZURE_OPENAI_ENDPOINT, API_KEY, MAX_TOKENS, TEMPERATURE

def load_qa_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def fuzzy_match_score(system_answer, reference_answer):
    if not system_answer or not reference_answer:
        return 0.0
    score = fuzz.partial_ratio(system_answer.lower(), reference_answer.lower()) / 100.0
    return score

def call_llm(prompt, model_name="gpt-3.5-turbo"):
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "model": model_name
    }
    try:
        response = requests.post(AZURE_OPENAI_ENDPOINT, json=payload, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            try:
                answer = resp_json["choices"][0]["message"]["content"]
                return answer.strip()
            except (KeyError, IndexError):
                return f"Unexpected response format: {resp_json}"
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return ""

def predict_probability_of_correctness(prompts, reference_answer):
    results = []
    for p in prompts:
        llm_ans = call_llm(p)
        score = fuzzy_match_score(llm_ans, reference_answer)
        p_correct = score
        p_incorrect = 1.0 - score
        results.append([p_incorrect, p_correct])
    return np.array(results)

def run_lime_explanation(question, knowledge_triples, reference_answer, num_samples=10):
    full_prompt = question + "\n" + "\n".join(knowledge_triples)
    explainer = LimeTextExplainer(class_names=["incorrect", "correct"])
    def predict_func(text_samples):
        return predict_probability_of_correctness(text_samples, reference_answer)
    exp = explainer.explain_instance(
        text_instance=full_prompt,
        classifier_fn=predict_func,
        labels=[1],
        num_samples=num_samples
    )
    local_explanation = exp.as_list(label=1)
    return local_explanation

def shap_model_predict(x, question, reference_answer, all_triples):
    results = []
    for row in x:
        included_triples = [all_triples[idx] for idx, val in enumerate(row) if val == 1]
        prompt = question + "\n" + "\n".join(included_triples)
        llm_ans = call_llm(prompt)
        score = fuzzy_match_score(llm_ans, reference_answer)
        results.append(score)
    return np.array(results)

def run_shap_explanation(question, knowledge_triples, reference_answer, nsamples=50):
    x0 = np.ones((1, len(knowledge_triples)), dtype=int)
    def predict_fn(x):
        return shap_model_predict(x, question, reference_answer, knowledge_triples)
    explainer = shap.KernelExplainer(model=predict_fn, data=x0)
    shap_values = explainer.shap_values(x0, nsamples=nsamples)
    sv = shap_values[0]
    results = []
    for i, triple in enumerate(knowledge_triples):
        val = sv[i]
        results.append({
            "triple": triple,
            "shap_value": float(val)
        })
    return results

def main():
    json_path = "results/results.json"
    output_path = "evaluation/results/explainability.json"
    if not os.path.exists(json_path):
        return
    data = load_qa_data(json_path)
    if not data:
        return
    analysis_results = []
    for idx, example in enumerate(data):
        question = example.get("question", "N/A")
        reference_answer = example.get("reference_answer", "")
        knowledge_facts = example.get("used_facts", [])
        triple_strings = [
            f"{fact.get('subject', '')} - {fact.get('relation', '')} - {fact.get('object', '')}"
            for fact in knowledge_facts
        ]
        lime_exp = run_lime_explanation(question, triple_strings, reference_answer, num_samples=10)
        shap_exp = run_shap_explanation(question, triple_strings, reference_answer, nsamples=50)
        analysis_results.append({
            "index": idx,
            "question": question,
            "reference_answer": reference_answer,
            "lime_explanation": lime_exp,
            "shap_explanation": shap_exp
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
