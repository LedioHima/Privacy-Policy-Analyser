# analyzer/detector.py
# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 & 6 of the pipeline: Detect → Classify
#
# Responsibilities:
#   - Scan every sentence against every pattern in RISK_CATEGORIES
#   - Return one Finding per (sentence × category) match
#   - Deduplicate: one sentence can trigger at most one finding per category
#     (the first matching pattern wins for that category)
# ─────────────────────────────────────────────────────────────────────────────

import re
from .models import Finding
from .risk_patterns import RISK_CATEGORIES


def detect_risks(sentences: list[str]) -> list[Finding]:
    """
    Scans every sentence against the full risk pattern dictionary.

    Algorithm:
      For each sentence:
        For each RiskCategory:
          Try each RiskPattern in order.
          On first match → record a Finding and move to the next category.
          (One sentence can match multiple categories, but each category
           is counted at most once per sentence to avoid inflating scores.)

    Args:
        sentences -- List of plain-text sentences from splitter.split_sentences()

    Returns:
        List of Finding objects, one per (sentence, category) match.
        Ordered by sentence position in the original document.
    """
    findings: list[Finding] = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        for category in RISK_CATEGORIES:
            for risk_pattern in category.patterns:
                match = re.search(risk_pattern.pattern, sentence_lower)
                if match:
                    findings.append(Finding(
                        sentence=sentence,
                        category=category.name,
                        severity=risk_pattern.severity,
                        plain_english=risk_pattern.plain_english,
                        pattern_matched=risk_pattern.pattern,
                    ))
                    break  # First matching pattern wins; move to next category

    return findings


def summarize_by_category(findings: list[Finding]) -> dict:
    """
    Groups findings by category and counts HIGH / MEDIUM severities.

    Args:
        findings -- List of Finding objects from detect_risks()

    Returns:
        Dict mapping category name → {"total": int, "high": int, "medium": int}

    Example:
        {
            "Data Selling & Third-Party Sharing": {"total": 3, "high": 3, "medium": 0},
            "Location Tracking":                  {"total": 1, "high": 1, "medium": 0},
            ...
        }
    """
    summary = {}
    for category in RISK_CATEGORIES:
        cat_findings = [f for f in findings if f.category == category.name]
        summary[category.name] = {
            "total":  len(cat_findings),
            "high":   sum(1 for f in cat_findings if f.severity == "HIGH"),
            "medium": sum(1 for f in cat_findings if f.severity == "MEDIUM"),
        }
    return summary
