# analyzer/scorer.py
# ─────────────────────────────────────────────────────────────────────────────
# Stage 7 of the pipeline: Score
#
# Converts a list of Finding objects into a single integer risk score (0–100)
# and a human-readable risk label.
#
# Algorithm overview:
#   1. For each category, compute a weighted sub-score:
#        sub = (high_count × weight × 1.0) + (medium_count × weight × 0.5)
#      Cap each category at 3× its weight to prevent one noisy category from
#      dominating the final score.
#   2. Sum all sub-scores and normalize to 0–100 against the theoretical
#      maximum (every category capped at 3× weight).
#   3. Add a density bonus (up to +10 pts) if a high proportion of sentences
#      are flagged — a policy with many risky clauses is riskier overall.
#   4. Clamp the result to [0, 100].
# ─────────────────────────────────────────────────────────────────────────────

from .models import Finding
from .risk_patterns import RISK_CATEGORIES

# Score thresholds for labeling
_THRESHOLDS = [
    (25,  "LOW RISK"),
    (50,  "MODERATE RISK"),
    (75,  "HIGH RISK"),
    (101, "CRITICAL RISK"),   # 101 so score == 100 is caught
]

# Multipliers per severity level
_SEVERITY_WEIGHT = {
    "HIGH":   1.0,
    "MEDIUM": 0.5,
}

# Maximum findings per category before the cap kicks in
_CAP_MULTIPLIER = 3

# Maximum density bonus points
_MAX_DENSITY_BONUS = 10


def calculate_risk_score(
    findings: list[Finding],
    total_sentences: int
) -> tuple[int, str]:
    """
    Calculates the overall privacy risk score for a policy.

    Args:
        findings         -- List of Finding objects from detector.detect_risks()
        total_sentences  -- Total number of sentences in the policy (for density)

    Returns:
        (score, label) tuple:
            score -- Integer in [0, 100]
            label -- One of: "LOW RISK", "MODERATE RISK", "HIGH RISK", "CRITICAL RISK"
    """
    if not findings:
        return 0, "LOW RISK"

    # ── Step 1: Per-category weighted sub-scores ──────────────────────────────
    total_weighted = 0.0
    max_possible   = 0.0

    for category in RISK_CATEGORIES:
        cat_findings = [f for f in findings if f.category == category.name]

        high_count = sum(1 for f in cat_findings if f.severity == "HIGH")
        med_count  = sum(1 for f in cat_findings if f.severity == "MEDIUM")

        raw_score = (
            high_count * category.weight * _SEVERITY_WEIGHT["HIGH"] +
            med_count  * category.weight * _SEVERITY_WEIGHT["MEDIUM"]
        )

        cap           = category.weight * _CAP_MULTIPLIER
        capped_score  = min(raw_score, cap)
        total_weighted += capped_score
        max_possible   += cap  # The cap IS the maximum for this category

    # ── Step 2: Normalize to 0–100 ────────────────────────────────────────────
    normalized = (total_weighted / max_possible) * 100 if max_possible > 0 else 0

    # ── Step 3: Density bonus ─────────────────────────────────────────────────
    # If > 5% of sentences are flagged, the policy is unusually risky.
    density       = len(findings) / max(total_sentences, 1)
    density_bonus = min(density * 100, _MAX_DENSITY_BONUS)

    # ── Step 4: Clamp ─────────────────────────────────────────────────────────
    final_score = min(int(normalized + density_bonus), 100)

    label = _score_to_label(final_score)
    return final_score, label


def _score_to_label(score: int) -> str:
    """Maps a numeric score to a human-readable risk label."""
    for threshold, label in _THRESHOLDS:
        if score < threshold:
            return label
    return "CRITICAL RISK"
