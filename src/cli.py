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

    summary = []

    for gold_j, pred_j in zip(gold_data, pred_data):
        metrics = compute_metrics(
            pred_j["items"],
            gold_j["items"]
        )
        summary.append({
            "journal_id": gold_j["journal_id"],
            **metrics
        })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
