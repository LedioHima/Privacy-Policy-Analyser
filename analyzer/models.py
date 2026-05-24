# analyzer/models.py
# ─────────────────────────────────────────────────────────────────────────────
# Data models for the Privacy Policy Analyzer.
# All dataclasses live here so every other module can import them without
# creating circular dependencies.
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field


@dataclass
class RiskPattern:
    """
    A single regex pattern that signals a risky clause.

    Attributes:
        pattern       -- Regex string to search for in a sentence
        plain_english -- Human-readable explanation shown to the user
        severity      -- Either "HIGH" or "MEDIUM"
    """
    pattern: str
    plain_english: str
    severity: str


@dataclass
class RiskCategory:
    """
    A named group of related RiskPatterns (e.g. all data-selling patterns).

    Attributes:
        name        -- Display name shown in reports
        description -- One-sentence summary of what this category covers
        patterns    -- List of RiskPattern objects belonging to this category
        weight      -- How much this category contributes to the 0–100 risk score
    """
    name: str
    description: str
    patterns: list[RiskPattern]
    weight: int


@dataclass
class Finding:
    """
    A single detected risky clause — produced by the detector for every match.

    Attributes:
        sentence        -- The full original sentence that was flagged
        category        -- Name of the RiskCategory that matched
        severity        -- "HIGH" or "MEDIUM" (copied from the matched pattern)
        plain_english   -- User-facing explanation of why this is risky
        pattern_matched -- The regex pattern that triggered this finding
    """
    sentence: str
    category: str
    severity: str
    plain_english: str
    pattern_matched: str


@dataclass
class AnalysisResult:
    """
    The complete result object returned after analyzing one privacy policy.

    Attributes:
        url              -- The URL or filename that was analyzed
        total_sentences  -- How many sentences the policy was split into
        findings         -- All Finding objects detected
        risk_score       -- Integer 0–100 overall privacy risk score
        risk_label       -- Human label: LOW / MODERATE / HIGH / CRITICAL RISK
        category_counts  -- Dict mapping category name → {total, high, medium}
        analyzed_at      -- Timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    url: str
    total_sentences: int
    findings: list[Finding]
    risk_score: int
    risk_label: str
    category_counts: dict
    analyzed_at: str
