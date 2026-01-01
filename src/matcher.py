def evidence_overlap(span_a: str, span_b: str) -> bool:
    """
    Returns True if one evidence span is a substring of the other.
    """
    a = span_a.lower()
    b = span_b.lower()
    return a in b or b in a


def match_items(predicted_items, gold_items):
    """
    Matches predicted items to gold items using:
    - identical domain
    - evidence span overlap

    Returns list of (pred_idx, gold_idx) tuples.
    """
    matches = []
    used_gold = set()

    for p_idx, pred in enumerate(predicted_items):
        for g_idx, gold in enumerate(gold_items):
            if g_idx in used_gold:
                continue

            if pred["domain"] != gold["domain"]:
                continue

            if evidence_overlap(pred["evidence_span"], gold["evidence_span"]):
                matches.append((p_idx, g_idx))
                used_gold.add(g_idx)
                break

    return matches
