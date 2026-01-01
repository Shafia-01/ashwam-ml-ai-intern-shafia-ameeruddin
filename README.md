# Ashwam - Exercise A: Evidence-Grounded Extraction & Evaluation

## Step 1: Extraction Schema
The extraction schema defines the structure of each extracted semantic item. It is designed to support safety, objective evaluation, and future extensibility without relying on canonical labels.

### Schema Overview
Each journal is represented by a `journal_id` and a list of extracted semantic items. Each semantic item corresponds to a single, evidence-backed claim found in the journal text.

### Constrained vs Free-Text Fields
The schema intentionally separates constrained categorical fields from free-text fields:

**Constrained fields**
- `domain`: symptom | food | emotion | mind
- `polarity`: present | absent | uncertain
- `intensity_bucket`: low | medium | high | unknown
- `arousal_bucket`: low | medium | high | unknown
- `time_bucket`: today | last_night | past_week | unknown

These constrained fields ensure deterministic outputs and enable objective, reproducible scoring without canonical vocabularies.

**Free-text fields**
- `evidence_span`: exact substring copied verbatim from the journal text
- `note` (optional): short human-readable clarification

Free-text fields preserve expressiveness while remaining grounded in source evidence.

### Safety Guarantees
Safety is enforced by requiring every extracted item to include an `evidence_span` that appears verbatim in the journal text. If no valid evidence span exists, the system abstains from extraction rather than hallucinating.

### Evaluation Support
The schema enables evaluation by:
- Matching predicted and gold items using domain and evidence span overlap
- Scoring polarity, intensity/arousal, and time using constrained categories

No semantic interpretation or label normalization is required.

### Extensibility
The schema is extensible: new attributes (e.g., duration, frequency, confidence) can be added without changing existing evaluation logic or invalidating prior outputs.

The full schema definition is provided in `schema.json`. The schema mirrors the structure used in the provided gold and prediction files (`items` per journal) to ensure compatibility with the evaluation harness.

## Step 2: Extraction Approach
### Overview
This exercise uses a deterministic, safety-first extraction approach focused on evidence grounding rather than recall. The goal is to extract semantic items only when there is explicit textual support in the journal entry.
No canonical vocabularies or medical ontologies are used.

- For this exercise, extraction outputs may be loaded from the provided `sample_predictions.jsonl`, and the focus is on the evaluation harness rather than model performance.

### Extraction Strategy
The extraction process is designed as a simple, deterministic pipeline:

1. Journal text is processed sentence-by-sentence.
2. Candidate spans are identified using lightweight pattern heuristics (e.g., negation phrases, temporal indicators, intensity adjectives).
3. A semantic item is created only when a verbatim evidence span can be copied directly from the journal text.

This approach avoids hallucinations and ensures reproducibility.

### Evidence Grounding
Every extracted item must include an `evidence_span` that:
- Is an exact substring of the original journal text
- Supports the extracted domain and attributes

If no such span can be found, no item is emitted.

### Polarity and Uncertainty Handling
Polarity is assigned conservatively:
- `present` only when the journal explicitly affirms the condition
- `absent` when explicit negation is present
- `uncertain` when language is ambiguous (e.g., "maybe", "not sure")

When uncertainty is detected, intensity and time buckets default to `unknown`.

### Determinism and Restraint
The extraction logic is deterministic:
- The same input journal always produces the same output
- No sampling or non-deterministic models are used

Restraint is prioritized over recall; it is preferable to abstain rather than
extract unsupported or speculative information.

## Step 3: Evaluation Method
The evaluation compares predicted semantic items against gold reference items without relying on canonical labels. Matching is based on evidence grounding and domain consistency.

### Item Matching Strategy
A predicted item is matched to a gold item if:
1. The `domain` field is identical, and
2. The `evidence_span` overlaps with the gold evidence span

Evidence overlap is computed using substring containment:
- A match is valid if one evidence span is a substring of the other

Each gold item can be matched to at most one predicted item (greedy matching).

### Definition of TP / FP / FN
- **True Positive (TP)**: a predicted item successfully matches a gold item
- **False Positive (FP)**: a predicted item that does not match any gold item
- **False Negative (FN)**: a gold item with no matching prediction

### Metrics Computed
The following metrics are computed at the item level:
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1 Score** = harmonic mean of precision and recall

### Attribute Accuracy
For matched items only:
- **Polarity accuracy**: exact match between predicted and gold polarity
- **Bucket accuracy**: exact match for intensity/arousal/time buckets
  - If either value is `unknown`, the comparison is excluded

### Evidence Coverage Rate
Evidence coverage is defined as the percentage of predicted items whose
`evidence_span` appears verbatim in the source journal text.

This metric ensures that extractions remain grounded in the input data.

Matching logic is implemented in `matcher.py`, while metric computation is handled in `scorer.py` to keep responsibilities separated.

## Step 4: Mock Evaluation
To demonstrate the evaluation logic, a mock evaluation is run on a small subset of journals (2–3 entries). Predicted items are compared against the gold reference items using the matching and scoring rules defined in Step 3.

The goal of this mock evaluation is to:
- Illustrate how items are matched
- Show how TP / FP / FN are derived
- Demonstrate metric computation in a transparent way

### Example Journal
Journal ID: J001  
Journal text excerpt: "..."

### Gold Item
```json
{
  "domain": "symptom",
  "evidence_span": "mild headache",
  "polarity": "present",
  "intensity_bucket": "low",
  "arousal_bucket": "unknown",
  "time_bucket": "last_night"
}
```

### Predicted Item
```json
{
  "domain": "symptom",
  "evidence_span": "headache",
  "polarity": "present",
  "intensity_bucket": "low",
  "arousal_bucket": "unknown",
  "time_bucket": "last_night"
}

```

### Matching Result
- Domains match (symptom)
- Evidence spans overlap ("headache" ⊂ "mild headache")
**Result**: Counted as **True Positive (TP)**

### Metric Outcome (Single Journal)
- TP = 1
- FP = 0
- FN = 0
- Precision = 1.0
- Recall = 1.0
- F1 = 1.0

This example demonstrates how evidence overlap enables objective evaluation without canonical labels while maintaining evidence grounding.

## Step 5: Failure Analysis
This section describes realistic failure modes observed in evidence-grounded extraction systems and how the proposed design detects or mitigates them.

### Failure Mode 1: Hallucinated Extraction
**Description**: The system emits an item that is not supported by the journal text.

**Why it happens**:
- Over-aggressive extraction heuristics
- Model speculation when evidence is weak or absent

**Mitigation**:
- Every extracted item must include an `evidence_span` that appears verbatim in the journal text
- Evidence coverage rate explicitly measures this failure mode
- If no valid evidence span exists, the system abstains
---
### Failure Mode 2: Incorrect Polarity Assignment
**Description**: Polarity is incorrectly marked as `present` when the journal contains negation or ambiguity.

**Why it happens**:
- Negation phrases ("not", "didn't", "no longer") are subtle
- Ambiguous language ("maybe", "kind of") is common in journals

**Mitigation**:
- Conservative polarity assignment
- Ambiguous language defaults to `uncertain`
- Polarity accuracy is computed only on matched items

---
### Failure Mode 3: Over-Splitting or Over-Merging Items
**Description**: A single journal statement is split into multiple redundant items, or multiple distinct statements are merged into one.

**Why it happens**:
- Heuristic span selection errors
- Lack of canonical labels to normalize concepts

**Mitigation**:
- Greedy one-to-one matching between predicted and gold items
- Object-level precision penalizes over-extraction
- Restraint is prioritized over recall

---
### Failure Mode 4: Bucket Misclassification
**Description**: Intensity, arousal, or time buckets are assigned incorrectly.

**Why it happens**:
- Implicit temporal references
- Subjective intensity language

**Mitigation**:
- Buckets default to `unknown` when unclear
- Bucket accuracy excludes comparisons involving `unknown`

---
## CLI Usage
The evaluation can be run using the following command:
```bash
python src/cli.py --gold data/gold.jsonl --pred data/sample_predictions.jsonl --out output/score_summary.json
```
This command loads gold references and predicted items, computes evaluation metrics, and writes results to disk.

### Output Files
The CLI produces the following outputs:
- `output/score_summary.json`: aggregated per-journal evaluation metrics
- `output/per_journal_scores.jsonl`: one JSON object per journal containing TP, FP,
  FN, precision, recall, and F1 scores

Predictions are matched to gold references by `journal_id`. Journals without predictions are evaluated with an empty predicted item set, resulting in false negatives only.
