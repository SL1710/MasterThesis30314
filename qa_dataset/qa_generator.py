import json

MAX_PER_CATEGORY = 50
gender_map = {
    "Q6581097": "male",
    "Q6581072": "female"
}
categories_counters = {
    "gender": 0,
    "birth_place": 0,
    "nationality": 0,
    "occupation": 0,
    "author": 0,
    "member_of": 0,
    "birth_date": 0,
    "ethnicity": 0,
    "religion": 0,
    "multi_hop": 0
}
all_seen_questions = set()

def is_all_categories_filled():
    return all(count >= MAX_PER_CATEGORY for count in categories_counters.values())

def lookup_label(qid, all_labels):
    if qid in gender_map:
        return gender_map[qid]
    return all_labels.get(qid, "Unknown label")

def build_qa_entries_for_item(item, all_labels):
    qa_entries = []
    label = item["label_en"]
    claims = item["claims"]
    if "P21" in claims and categories_counters["gender"] < MAX_PER_CATEGORY:
        seen_labels_p21 = set()
        for qid in claims["P21"]:
            if categories_counters["gender"] >= MAX_PER_CATEGORY:
                break
            gender_str = lookup_label(qid, all_labels)
            if gender_str == "Unknown label":
                continue
            if gender_str in seen_labels_p21:
                continue
            question = f"What is the gender of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} gender -> {gender_str}."
            answer = gender_str.capitalize() + "."
            explanation = f"P21 indicates {gender_str}."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p21.add(gender_str)
            all_seen_questions.add(question)
            categories_counters["gender"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P19" in claims and categories_counters["birth_place"] < MAX_PER_CATEGORY:
        seen_labels_p19 = set()
        for qid in claims["P19"]:
            if categories_counters["birth_place"] >= MAX_PER_CATEGORY:
                break
            place = lookup_label(qid, all_labels)
            if place == "Unknown label":
                continue
            if place in seen_labels_p19:
                continue
            question = f"Where was {label} born?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} birth place -> {place}."
            answer = place
            explanation = "P19 indicates the place of birth."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p19.add(place)
            all_seen_questions.add(question)
            categories_counters["birth_place"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P27" in claims and categories_counters["nationality"] < MAX_PER_CATEGORY:
        seen_labels_p27 = set()
        for qid in claims["P27"]:
            if categories_counters["nationality"] >= MAX_PER_CATEGORY:
                break
            country = lookup_label(qid, all_labels)
            if country == "Unknown label":
                continue
            if country in seen_labels_p27:
                continue
            question = f"What is the nationality of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} nationality -> {country}."
            answer = country
            explanation = "P27 indicates the nationality."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p27.add(country)
            all_seen_questions.add(question)
            categories_counters["nationality"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P106" in claims and categories_counters["occupation"] < MAX_PER_CATEGORY:
        seen_labels_p106 = set()
        for qid in claims["P106"]:
            if categories_counters["occupation"] >= MAX_PER_CATEGORY:
                break
            occ = lookup_label(qid, all_labels)
            if occ == "Unknown label":
                continue
            if occ in seen_labels_p106:
                continue
            question = f"What is the occupation of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} occupation -> {occ}."
            answer = occ
            explanation = "P106 indicates the occupation."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p106.add(occ)
            all_seen_questions.add(question)
            categories_counters["occupation"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P50" in claims and categories_counters["author"] < MAX_PER_CATEGORY:
        seen_labels_p50 = set()
        for qid in claims["P50"]:
            if categories_counters["author"] >= MAX_PER_CATEGORY:
                break
            author_label = lookup_label(qid, all_labels)
            if author_label == "Unknown label":
                continue
            if author_label in seen_labels_p50:
                continue
            question = f"Who is the author of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} author -> {author_label}."
            answer = author_label
            explanation = "P50 indicates the author."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p50.add(author_label)
            all_seen_questions.add(question)
            categories_counters["author"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P463" in claims and categories_counters["member_of"] < MAX_PER_CATEGORY:
        seen_labels_p463 = set()
        for qid in claims["P463"]:
            if categories_counters["member_of"] >= MAX_PER_CATEGORY:
                break
            member_of_str = lookup_label(qid, all_labels)
            if member_of_str == "Unknown label":
                continue
            if member_of_str in seen_labels_p463:
                continue
            question = f"Which organization is {label} a member of?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} is member of -> {member_of_str}."
            answer = member_of_str
            explanation = "P463 indicates membership."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p463.add(member_of_str)
            all_seen_questions.add(question)
            categories_counters["member_of"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P569" in claims and categories_counters["birth_date"] < MAX_PER_CATEGORY:
        seen_dates = set()
        for date_str in claims["P569"]:
            if categories_counters["birth_date"] >= MAX_PER_CATEGORY:
                break
            if date_str.startswith("+"):
                date_str = date_str[1:]
            date_str = date_str.split("T")[0].rstrip("Z")
            if date_str in seen_dates:
                continue
            seen_dates.add(date_str)
            question = f"When was {label} born?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} birth date -> {date_str}."
            answer = date_str
            explanation = "P569 indicates the date of birth."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            all_seen_questions.add(question)
            categories_counters["birth_date"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P172" in claims and categories_counters["ethnicity"] < MAX_PER_CATEGORY:
        seen_labels_p172 = set()
        for qid in claims["P172"]:
            if categories_counters["ethnicity"] >= MAX_PER_CATEGORY:
                break
            eth_str = lookup_label(qid, all_labels)
            if eth_str == "Unknown label":
                continue
            if eth_str in seen_labels_p172:
                continue
            question = f"What is the ethnicity of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} ethnicity -> {eth_str}."
            answer = eth_str
            explanation = "P172 indicates the ethnicity."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p172.add(eth_str)
            all_seen_questions.add(question)
            categories_counters["ethnicity"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P140" in claims and categories_counters["religion"] < MAX_PER_CATEGORY:
        seen_labels_p140 = set()
        for qid in claims["P140"]:
            if categories_counters["religion"] >= MAX_PER_CATEGORY:
                break
            rel_str = lookup_label(qid, all_labels)
            if rel_str == "Unknown label":
                continue
            if rel_str in seen_labels_p140:
                continue
            question = f"What is the religion of {label}?"
            if question in all_seen_questions:
                continue
            knowledge_snippet = f"{label} religion -> {rel_str}."
            answer = rel_str
            explanation = "P140 indicates the religion."
            qa_entries.append({
                "question": question,
                "knowledge_snippet": knowledge_snippet,
                "answer": answer,
                "explanation": explanation
            })
            seen_labels_p140.add(rel_str)
            all_seen_questions.add(question)
            categories_counters["religion"] += 1
            if is_all_categories_filled():
                return qa_entries
    if "P569" in claims and "P27" in claims and categories_counters["multi_hop"] < MAX_PER_CATEGORY:
        date_values = claims["P569"]
        country_values = claims["P27"]
        if date_values and country_values:
            date_str = date_values[0]
            if date_str.startswith("+"):
                date_str = date_str[1:]
            date_str = date_str.split("T")[0].rstrip("Z")
            country_qid = country_values[0]
            country_label = lookup_label(country_qid, all_labels)
            if country_label != "Unknown label":
                question = f"When was {label} born and what is their nationality?"
                if question not in all_seen_questions:
                    knowledge_snippet = f"{label} birth date -> {date_str}, nationality -> {country_label}."
                    answer = f"{label} was born on {date_str} and is {country_label}."
                    explanation = "P569 indicates birth date, P27 indicates nationality."
                    qa_entries.append({
                        "question": question,
                        "knowledge_snippet": knowledge_snippet,
                        "answer": answer,
                        "explanation": explanation
                    })
                    all_seen_questions.add(question)
                    categories_counters["multi_hop"] += 1
    return qa_entries

def main():
    input_file = "knowledge_graph/sliced/kg_sliced.json"
    output_file = "qa_Dataset/qa_data.json"
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_labels = {}
    for item in data:
        qid = item["id"]
        all_labels[qid] = item["label_en"]
    qa_dataset = []
    for item in data:
        if is_all_categories_filled():
            break
        new_qas = build_qa_entries_for_item(item, all_labels)
        qa_dataset.extend(new_qas)
        if is_all_categories_filled():
            break
    with open(output_file, "w", encoding="utf-8") as f_out:
        json.dump({"qa_dataset": qa_dataset}, f_out, ensure_ascii=False, indent=2)
    print(f"Total Q&A: {len(qa_dataset)}")
    for cat, cnt in categories_counters.items():
        print(f"{cat}: {cnt}")

if __name__ == "__main__":
    main()
