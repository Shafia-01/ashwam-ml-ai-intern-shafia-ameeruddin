import json
import argparse
from scorer import compute_metrics

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--pred", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    gold_data = load_jsonl(args.gold)
    pred_data = load_jsonl(args.pred)

    # Index predictions by journal_id
    pred_by_id = {
        p["journal_id"]: p.get("items", [])
        for p in pred_data
    }

    per_journal = []

    for gold_j in gold_data:
        journal_id = gold_j["journal_id"]
        gold_items = gold_j["items"]

        pred_items = pred_by_id.get(journal_id, [])

        metrics = compute_metrics(pred_items, gold_items)

        per_journal.append({
            "journal_id": journal_id,
            **metrics
        })

    # Write per-journal scores (JSONL)
    with open("output/per_journal_scores.jsonl", "w", encoding="utf-8") as f:
        for row in per_journal:
            f.write(json.dumps(row) + "\n")

    # Write summary scores (JSON)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(per_journal, f, indent=2)

if __name__ == "__main__":
    main()
