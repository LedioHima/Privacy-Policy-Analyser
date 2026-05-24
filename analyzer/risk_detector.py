"""
Privacy Policy Analyzer - Week 2: Risk Detection Engine
=========================================================
Reads sentences from Week 1 output (or runs the full pipeline from a URL),
detects risky clauses across 7 risk categories using keyword pattern matching,
assigns severity levels, calculates an overall privacy risk score (0–100),
and prints a detailed color-coded report.

Dependencies (same as Week 1, nothing new to install):
    pip install requests beautifulsoup4 spacy lxml
    python -m spacy download en_core_web_sm

Usage:
    # Analyze from a URL directly (runs Week 1 pipeline automatically):
    python risk_detector.py https://policies.google.com/privacy

    # Analyze from an already-saved sentences file:
    python risk_detector.py --file policy_sentences.txt
"""

import re
import sys
import json
from dataclasses import dataclass, field
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# WEEK 1 PIPELINE — imported inline so this file is self-contained
# ─────────────────────────────────────────────────────────────────

import requests
import spacy
from bs4 import BeautifulSoup


def fetch_policy(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    print(f"[+] Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    print(f"[+] Fetched {len(response.text):,} characters of HTML")
    return response.text


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "button"]):
        tag.decompose()
    raw_text = soup.get_text(separator=" ")
    cleaned = re.sub(r'\s+', ' ', raw_text).strip()
    print(f"[+] Cleaned to {len(cleaned):,} characters of plain text")
    return cleaned


def split_sentences(text: str) -> list[str]:
    print("[+] Running NLP sentence splitting...")
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 1_000_000
    doc = nlp(text[:1_000_000])
    sentences = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 20]
    print(f"[+] Split into {len(sentences):,} sentences")
    return sentences


# ─────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────

@dataclass
class RiskPattern:
    """A single keyword/phrase pattern that signals a risky clause."""
    pattern: str          # Regex pattern to match
    plain_english: str    # Human-readable explanation of why this is risky
    severity: str         # "HIGH" or "MEDIUM"


@dataclass
class RiskCategory:
    """A group of related patterns (e.g. all data-selling patterns)."""
    name: str
    description: str
    patterns: list[RiskPattern]
    weight: int           # How much this category contributes to the risk score


@dataclass
class Finding:
    """A single detected risky clause."""
    sentence: str
    category: str
    severity: str
    plain_english: str
    pattern_matched: str


@dataclass
class AnalysisResult:
    """The complete result of analyzing one privacy policy."""
    url: str
    total_sentences: int
    findings: list[Finding]
    risk_score: int
    risk_label: str
    category_counts: dict
    analyzed_at: str


# ─────────────────────────────────────────────────────────────────
# KEYWORD DICTIONARY — The academic core of Week 2
# Each pattern is a carefully chosen regex that matches risky language
# while avoiding false positives.
# ─────────────────────────────────────────────────────────────────

RISK_CATEGORIES: list[RiskCategory] = [

    RiskCategory(
        name="Data Selling & Third-Party Sharing",
        description="The company sells or shares your personal data with external parties.",
        weight=25,
        patterns=[
            RiskPattern(
                r"\bsell\b.{0,40}\b(data|information|profile|records)\b",
                "This policy explicitly states they may SELL your personal data.",
                "HIGH"
            ),
            RiskPattern(
                r"\bshare\b.{0,60}\b(third.part|partner|affiliate|advertis)",
                "Your data is shared with third-party partners, likely for advertising.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(transfer|disclose|provide).{0,50}\b(third.part|outside|external)",
                "Your data may be transferred or disclosed to outside organizations.",
                "HIGH"
            ),
            RiskPattern(
                r"\bmonetize\b.{0,40}\b(data|information|user)",
                "The company explicitly monetizes (makes money from) your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\badvertising partner|marketing partner|data broker",
                "Your data is shared with advertising or data broker networks.",
                "HIGH"
            ),
            RiskPattern(
                r"\bshare.{0,40}\bfor (marketing|advertising|commercial)",
                "Your data is shared specifically for marketing or advertising purposes.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="Location Tracking",
        description="The company collects your physical location data.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\b(precise|exact|real.time|continuous).{0,30}\b(location|gps|geolocation)",
                "Your precise or real-time GPS location is being tracked.",
                "HIGH"
            ),
            RiskPattern(
                r"\bcollect.{0,40}\b(location|gps|geolocation|coordinates)",
                "The company collects your location data.",
                "HIGH"
            ),
            RiskPattern(
                r"\btrack.{0,40}\b(location|movement|whereabouts|physical)",
                "Your physical movements or whereabouts may be tracked.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(ip address|wi.fi|bluetooth).{0,40}\b(location|infer|derive|estimate)",
                "Your location is inferred from your IP address, Wi-Fi, or Bluetooth signals.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bgeofenc|location.based service|location history",
                "The company uses geofencing or stores your location history.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="Indefinite Data Retention",
        description="The company keeps your data indefinitely or for vague time periods.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\bretain.{0,50}\b(as long as (necessary|needed|required)|indefinitely|forever)",
                "Your data is kept for an undefined or unlimited period of time.",
                "HIGH"
            ),
            RiskPattern(
                r"\bkeep.{0,50}\b(as long as|until|indefinitely|no set|no specific)",
                "There is no clear deletion schedule — data may be kept indefinitely.",
                "HIGH"
            ),
            RiskPattern(
                r"\bno.{0,20}(expir|delet|remov).{0,30}(schedul|date|polic)",
                "There is no expiration or scheduled deletion policy for your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\barchiv.{0,40}\b(indefinitely|permanently|long.term)",
                "Your data is archived permanently or for the long term.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bretention period.{0,40}(not|no|undefined|unspecified|varies)",
                "The data retention period is unspecified or varies without clear rules.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="No Right to Deletion",
        description="Users cannot delete their account or request data removal.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\bcannot.{0,40}\b(delete|remove|erase).{0,30}\b(account|data|information)",
                "You are explicitly told you CANNOT delete your data or account.",
                "HIGH"
            ),
            RiskPattern(
                r"\bno.{0,20}(right|option|ability).{0,30}\b(delet|remov|eras)",
                "There is no right or option provided to delete your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(waive|forfeit|relinquish).{0,40}\b(right|claim).{0,30}\b(data|privacy|delet)",
                "You are asked to waive your data rights, including the right to deletion.",
                "HIGH"
            ),
            RiskPattern(
                r"\bdeletion request.{0,40}(may be denied|not guaranteed|not obligated)",
                "Deletion requests may be denied without clear reason.",
                "HIGH"
            ),
            RiskPattern(
                r"\bsome (data|information).{0,40}(cannot|may not).{0,30}(be deleted|be removed)",
                "Some of your data cannot be deleted even if you request it.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="Behavioral Profiling",
        description="The company builds personal profiles based on your behavior and activity.",
        weight=15,
        patterns=[
            RiskPattern(
                r"\b(build|creat|develop|maintain).{0,40}\b(profile|profil)",
                "The company builds a behavioral profile about you.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(track|monitor|record).{0,40}\b(browsing|behavior|activity|habit|interest)",
                "Your browsing behavior, habits, and interests are being tracked.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\binfer.{0,40}\b(interest|preference|characteristic|attribute)",
                "The company makes inferences about your personality, interests, or preferences.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bbehavioral.{0,30}(advertis|target|data|analytic)",
                "You are targeted with behavioral advertising based on tracked activity.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(cross.site|cross.platform|cross.device).{0,30}(track|monitor|follow)",
                "Your activity is tracked across multiple websites, platforms, or devices.",
                "HIGH"
            ),
            RiskPattern(
                r"\bfingerprint(ing)?.{0,30}(device|browser|user)",
                "Your device or browser is fingerprinted to identify you without cookies.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="Children's Data Collection",
        description="The company collects data from or about children under 13.",
        weight=25,
        patterns=[
            RiskPattern(
                r"\b(collect|process|use).{0,50}\b(child|minor|under.13|under 13|coppa)",
                "The policy addresses data collection from children — requires careful review.",
                "HIGH"
            ),
            RiskPattern(
                r"\bchild(ren)?.{0,40}(data|information|privacy)",
                "The company handles children's data — check if proper safeguards exist.",
                "HIGH"
            ),
            RiskPattern(
                r"\bunder.{0,10}(13|sixteen|18|eighteen).{0,30}(collect|use|share|data)",
                "Data is collected from users under a certain age — a legal red flag.",
                "HIGH"
            ),
            RiskPattern(
                r"\bparental consent.{0,40}(not required|may not|waived)",
                "Parental consent requirements may not be enforced for minors.",
                "HIGH"
            ),
        ]
    ),

    RiskCategory(
        name="Law Enforcement & Government Sharing",
        description="The company shares your data with government agencies or law enforcement.",
        weight=15,
        patterns=[
            RiskPattern(
                r"\b(law enforcement|government|authorit|agenc).{0,50}\b(request|demand|order|require)",
                "Your data may be handed over to law enforcement or government agencies on request.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(share|disclose|provide).{0,50}\b(law enforcement|government|court|legal process)",
                "Data is disclosed to courts, law enforcement, or in legal proceedings.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(subpoena|court order|legal obligation|national security)",
                "Data can be shared under subpoena, court order, or national security requests.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bwithout.{0,30}(notice|notif|warrant|your knowledge)",
                "Your data can be shared with authorities without notifying you.",
                "HIGH"
            ),
            RiskPattern(
                r"\bvoluntarily.{0,40}\b(share|cooperat|assist).{0,30}(government|law enforcement|authorit)",
                "The company voluntarily assists government agencies beyond what is legally required.",
                "HIGH"
            ),
        ]
    ),
]


# ─────────────────────────────────────────────────────────────────
# DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────

def detect_risks(sentences: list[str]) -> list[Finding]:
    """
    Scans every sentence against every pattern in every risk category.
    Returns a list of Finding objects for all matches.
    Deduplicates: one sentence can only trigger one finding per category.
    """
    findings = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        for category in RISK_CATEGORIES:
            # Track if this sentence already matched this category (avoid duplicates)
            already_matched_category = False

            for risk_pattern in category.patterns:
                if already_matched_category:
                    break

                match = re.search(risk_pattern.pattern, sentence_lower)
                if match:
                    findings.append(Finding(
                        sentence=sentence,
                        category=category.name,
                        severity=risk_pattern.severity,
                        plain_english=risk_pattern.plain_english,
                        pattern_matched=risk_pattern.pattern
                    ))
                    already_matched_category = True

    return findings


# ─────────────────────────────────────────────────────────────────
# RISK SCORING ALGORITHM
# ─────────────────────────────────────────────────────────────────

def calculate_risk_score(findings: list[Finding], total_sentences: int) -> tuple[int, str]:
    """
    Calculates a risk score from 0 to 100 using a weighted algorithm.

    Algorithm:
    - Each HIGH finding in a category contributes its category weight × 1.0
    - Each MEDIUM finding contributes its category weight × 0.5
    - Score is normalized to 0–100 using the maximum possible score
    - Bonus points for finding density (many risky sentences = riskier policy)

    Returns (score, label) where label is one of:
        "LOW RISK", "MODERATE RISK", "HIGH RISK", "CRITICAL RISK"
    """
    if not findings:
        return 0, "LOW RISK"

    # Build per-category score
    category_scores = {}
    for category in RISK_CATEGORIES:
        cat_findings = [f for f in findings if f.category == category.name]
        high_count = sum(1 for f in cat_findings if f.severity == "HIGH")
        med_count  = sum(1 for f in cat_findings if f.severity == "MEDIUM")

        # Each unique high/medium finding adds points, capped at 3× weight per category
        raw = (high_count * category.weight * 1.0) + (med_count * category.weight * 0.5)
        capped = min(raw, category.weight * 3)
        category_scores[category.name] = capped

    base_score = sum(category_scores.values())

    # Maximum possible score: all categories at cap (3× weight)
    max_possible = sum(c.weight * 3 for c in RISK_CATEGORIES)

    # Normalize to 0–100
    normalized = (base_score / max_possible) * 100

    # Density bonus: if >5% of sentences are flagged, add up to 10 points
    density = len(findings) / max(total_sentences, 1)
    density_bonus = min(density * 100, 10)  # max 10 bonus points

    final_score = min(int(normalized + density_bonus), 100)

    # Label
    if final_score < 25:
        label = "LOW RISK"
    elif final_score < 50:
        label = "MODERATE RISK"
    elif final_score < 75:
        label = "HIGH RISK"
    else:
        label = "CRITICAL RISK"

    return final_score, label


# ─────────────────────────────────────────────────────────────────
# REPORT PRINTER — Color-coded terminal output
# ─────────────────────────────────────────────────────────────────

# ANSI color codes for terminal output
RED     = "\033[91m"
ORANGE  = "\033[38;5;208m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
RESET   = "\033[0m"
WHITE   = "\033[97m"
MAGENTA = "\033[95m"


def severity_color(severity: str) -> str:
    return RED if severity == "HIGH" else YELLOW


def score_color(score: int) -> str:
    if score < 25:
        return GREEN
    elif score < 50:
        return YELLOW
    elif score < 75:
        return ORANGE
    else:
        return RED


def print_report(result: AnalysisResult):
    """Prints a full color-coded risk report to the terminal."""

    W = 70  # Report width

    print("\n" + "═" * W)
    print(f"{BOLD}{CYAN}  PRIVACY POLICY RISK ANALYSIS REPORT{RESET}")
    print("═" * W)
    print(f"  URL       : {result.url}")
    print(f"  Analyzed  : {result.analyzed_at}")
    print(f"  Sentences : {result.total_sentences:,} total  |  {len(result.findings)} risky clauses found")
    print("─" * W)

    # Risk Score Block
    sc = score_color(result.risk_score)
    print(f"\n  {BOLD}OVERALL PRIVACY RISK SCORE{RESET}")
    print(f"\n  {sc}{BOLD}  {result.risk_score} / 100  —  {result.risk_label}  {RESET}\n")

    # Score bar
    filled = result.risk_score // 5
    bar = "█" * filled + "░" * (20 - filled)
    print(f"  [{sc}{bar}{RESET}]")
    print(f"   0 (Safe){'':>30}100 (Dangerous)")
    print()

    # Per-category summary
    print("─" * W)
    print(f"  {BOLD}FINDINGS BY CATEGORY{RESET}\n")

    for category in RISK_CATEGORIES:
        cat_findings = [f for f in result.findings if f.category == category.name]
        high = sum(1 for f in cat_findings if f.severity == "HIGH")
        med  = sum(1 for f in cat_findings if f.severity == "MEDIUM")
        total = len(cat_findings)

        if total == 0:
            icon = f"{GREEN}✓{RESET}"
            label = f"{GREEN}Clean{RESET}"
        elif high > 0:
            icon = f"{RED}✗{RESET}"
            label = f"{RED}{high} HIGH{RESET}" + (f", {YELLOW}{med} MEDIUM{RESET}" if med else "")
        else:
            icon = f"{YELLOW}⚠{RESET}"
            label = f"{YELLOW}{med} MEDIUM{RESET}"

        print(f"  {icon}  {BOLD}{category.name:<38}{RESET}  {label}")

    # Detailed findings
    if result.findings:
        print()
        print("─" * W)
        print(f"  {BOLD}DETAILED FLAGGED CLAUSES{RESET}\n")

        for i, finding in enumerate(result.findings, start=1):
            sc2 = severity_color(finding.severity)
            print(f"  {BOLD}[{i:>2}] {sc2}{'■ ' + finding.severity:<10}{RESET}  {CYAN}{finding.category}{RESET}")
            print(f"       {BOLD}Why it's risky:{RESET} {finding.plain_english}")

            # Truncate long sentences for readability
            sentence_display = finding.sentence if len(finding.sentence) <= 200 else finding.sentence[:200] + "..."
            print(f"       {WHITE}Clause:{RESET} \"{sentence_display}\"")
            print()

    # GDPR quick check
    print("─" * W)
    print(f"  {BOLD}GDPR COMPLIANCE QUICK CHECK{RESET}\n")

    gdpr_checks = [
        ("Right to Deletion",    "No Right to Deletion"),
        ("Data Selling Banned",  "Data Selling & Third-Party Sharing"),
        ("Children Protection",  "Children's Data Collection"),
        ("Location Consent",     "Location Tracking"),
    ]

    for check_name, category_name in gdpr_checks:
        cat_hits = [f for f in result.findings if f.category == category_name]
        if cat_hits:
            print(f"  {RED}✗  {check_name}: Potential violation detected{RESET}")
        else:
            print(f"  {GREEN}✓  {check_name}: No issues found{RESET}")

    print()
    print("═" * W)
    print(f"  {BOLD}Report complete.{RESET} Results saved to: risk_report.json")
    print("═" * W + "\n")


# ─────────────────────────────────────────────────────────────────
# SAVE REPORT — Export findings to JSON for Week 3 backend
# ─────────────────────────────────────────────────────────────────

def save_report(result: AnalysisResult, output_file: str = "risk_report.json"):
    """
    Saves the full analysis result to a JSON file.
    This will be read by the Week 3 Flask backend to serve the frontend.
    """
    data = {
        "url": result.url,
        "analyzed_at": result.analyzed_at,
        "total_sentences": result.total_sentences,
        "risk_score": result.risk_score,
        "risk_label": result.risk_label,
        "total_findings": len(result.findings),
        "category_counts": result.category_counts,
        "findings": [
            {
                "sentence": f.sentence,
                "category": f.category,
                "severity": f.severity,
                "plain_english": f.plain_english,
            }
            for f in result.findings
        ]
    }
    with open(output_file, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)

    print(f"[+] JSON report saved to: {output_file}")


# ─────────────────────────────────────────────────────────────────
# MAIN ANALYSIS FUNCTION
# ─────────────────────────────────────────────────────────────────

def analyze(url_or_file: str, is_file: bool = False) -> AnalysisResult:
    """
    Full Week 2 pipeline:
    Sentences → Detect risks → Score → Report → Save
    """
    print("\n" + "=" * 70)
    print("  PRIVACY POLICY ANALYZER — Week 2: Risk Detection Engine")
    print("=" * 70 + "\n")

    # ── Get sentences ──────────────────────────────────────────────
    if is_file:
        print(f"[+] Reading sentences from file: {url_or_file}")
        with open(url_or_file, "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if len(line.strip()) > 20]
        print(f"[+] Loaded {len(sentences):,} sentences")
        url_label = url_or_file
    else:
        html = fetch_policy(url_or_file)
        text = clean_html(html)
        sentences = split_sentences(text)
        url_label = url_or_file

    # ── Detect risky clauses ───────────────────────────────────────
    print(f"[+] Scanning {len(sentences):,} sentences across {len(RISK_CATEGORIES)} risk categories...")
    findings = detect_risks(sentences)
    print(f"[+] Found {len(findings)} risky clauses")

    # ── Score ──────────────────────────────────────────────────────
    risk_score, risk_label = calculate_risk_score(findings, len(sentences))

    # ── Category counts for summary ───────────────────────────────
    category_counts = {}
    for category in RISK_CATEGORIES:
        cat_findings = [f for f in findings if f.category == category.name]
        category_counts[category.name] = {
            "total": len(cat_findings),
            "high":  sum(1 for f in cat_findings if f.severity == "HIGH"),
            "medium": sum(1 for f in cat_findings if f.severity == "MEDIUM"),
        }

    # ── Build result object ────────────────────────────────────────
    result = AnalysisResult(
        url=url_label,
        total_sentences=len(sentences),
        findings=findings,
        risk_score=risk_score,
        risk_label=risk_label,
        category_counts=category_counts,
        analyzed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # ── Print report ───────────────────────────────────────────────
    print_report(result)

    # ── Save JSON ──────────────────────────────────────────────────
    save_report(result)

    return result


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Usage examples:
        python risk_detector.py
        python risk_detector.py https://policies.google.com/privacy
        python risk_detector.py https://www.facebook.com/privacy/policy/
        python risk_detector.py --file policy_sentences.txt
    """
    if len(sys.argv) == 3 and sys.argv[1] == "--file":
        analyze(sys.argv[2], is_file=True)

    elif len(sys.argv) == 2:
        analyze(sys.argv[1])

    else:
        # Default: run on Google's privacy policy
        analyze("https://policies.google.com/privacy")
