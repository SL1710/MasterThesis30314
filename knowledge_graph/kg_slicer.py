import bz2
import json

def preprocess_wikidata(input_bz2_file="knowledge_graph/raw/latest-all.json.bz2", output_json_file="knowledge_graph/sliced/kg_sliced.json", max_items=None):
    target_ids = {"Q5", "Q43229", "Q6256"}
    properties_of_interest = {
        "P31","P279","P21","P19","P569","P27","P106","P172","P140",
        "P17","P131","P50","P123"
    }
    count_written = 0
    with bz2.open(input_bz2_file, "rt", encoding="utf-8") as fin, open(output_json_file, "w", encoding="utf-8") as fout:
        fout.write("[\n")
        first_item = True
        for line in fin:
            line = line.strip()
            if not line or line in ["[", "]", ","]:
                continue
            try:
                data = json.loads(line.rstrip(","))
            except json.JSONDecodeError:
                continue
            labels = data.get("labels", {})
            if "en" not in labels:
                continue
            claims = data.get("claims", {})
            if not claims:
                continue
            is_in_focus = False
            for prop_id in ["P31", "P279"]:
                if prop_id in claims:
                    for statement in claims[prop_id]:
                        mainsnak = statement.get("mainsnak", {})
                        datavalue = mainsnak.get("datavalue", {})
                        if datavalue.get("type") == "wikibase-entityid":
                            target_id = datavalue["value"].get("id", "")
                            if target_id in target_ids:
                                is_in_focus = True
                                break
                if is_in_focus:
                    break
            if not is_in_focus:
                continue
            extracted_claims = {}
            for prop_id, statement_list in claims.items():
                if prop_id not in properties_of_interest:
                    continue
                extracted_values = []
                for statement in statement_list:
                    mainsnak = statement.get("mainsnak", {})
                    datavalue = mainsnak.get("datavalue", {})
                    value_type = datavalue.get("type")
                    if value_type == "wikibase-entityid":
                        qid = datavalue["value"].get("id")
                        if qid:
                            extracted_values.append(qid)
                    elif value_type == "time":
                        time_str = datavalue["value"].get("time")
                        if time_str:
                            extracted_values.append(time_str)
                if extracted_values:
                    extracted_claims[prop_id] = extracted_values
            item_id = data.get("id", "")
            label_en = labels["en"].get("value", "")
            desc_en = data.get("descriptions", {}).get("en", {}).get("value", "")
            minimal_item = {
                "id": item_id,
                "label_en": label_en,
                "description_en": desc_en,
                "claims": extracted_claims
            }
            if not first_item:
                fout.write(",\n")
            json.dump(minimal_item, fout, ensure_ascii=False)
            first_item = False
            count_written += 1
            if max_items and count_written >= max_items:
                break
        fout.write("\n]\n")
    print(f"Fertig. Insgesamt {count_written} Einträge nach '{output_json_file}' geschrieben.")

if __name__ == "__main__":
    preprocess_wikidata(
        input_bz2_file="knowledge_graph/raw/latest-all.json.bz2",
        output_json_file="knowledge_graph/sliced/kg_sliced.json",
        max_items=None
    )
