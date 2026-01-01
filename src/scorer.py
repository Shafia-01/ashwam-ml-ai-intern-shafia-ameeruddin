from matcher import match_items

def compute_metrics(predicted_items, gold_items):
    matches = match_items(predicted_items, gold_items)

    tp = len(matches)
    fp = len(predicted_items) - tp
    fn = len(gold_items) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
