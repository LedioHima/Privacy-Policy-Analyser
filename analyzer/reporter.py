# analyzer/reporter.py
# ─────────────────────────────────────────────────────────────────────────────
# Stage 8 of the pipeline: Present
#
# Responsibilities:
#   - Print a color-coded risk report to the terminal (human-readable)
#   - Export findings to a JSON file (machine-readable, consumed by the REST API)
#
# Color coding:
#   RED    → HIGH severity finding or high risk score
#   YELLOW → MEDIUM severity finding or moderate risk score
#   GREEN  → No findings / low risk score
#   CYAN   → Category names and section headers
# ─────────────────────────────────────────────────────────────────────────────

import json
from .models import AnalysisResult, Finding
from .risk_patterns import RISK_CATEGORIES

# ── ANSI terminal color codes ─────────────────────────────────────────────────
RED     = "\033[91m"
ORANGE  = "\033[38;5;208m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

_REPORT_WIDTH = 70


# ── Internal helpers ──────────────────────────────────────────────────────────

def _severity_color(severity: str) -> str:
    return RED if severity == "HIGH" else YELLOW


def _score_color(score: int) -> str:
    if score < 25:
        return GREEN
    elif score < 50:
        return YELLOW
    elif score < 75:
        return ORANGE
    else:
        return RED


def _score_bar(score: int, width: int = 20) -> str:
    """Returns a filled/empty block progress bar string."""
    filled = score // (100 // width)
    return "█" * filled + "░" * (width - filled)


def _truncate(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[:max_len] + "..."


# ── Public functions ──────────────────────────────────────────────────────────

def print_report(result: AnalysisResult) -> None:
    """
    Prints a full color-coded risk report to the terminal.

    Sections:
      1. Header — URL, timestamp, sentence count, finding count
      2. Risk score — numeric score, label, visual bar
      3. Category summary — one line per category with hit counts
      4. Detailed findings — each flagged clause with plain-English explanation
      5. GDPR quick check — pass/fail for four key GDPR requirements

    Args:
        result -- Completed AnalysisResult from pipeline.run()
    """
    W = _REPORT_WIDTH

    # ── Header ────────────────────────────────────────────────────────────────
    print("\n" + "═" * W)
    print(f"{BOLD}{CYAN}  PRIVACY POLICY RISK ANALYSIS REPORT{RESET}")
    print("═" * W)
    print(f"  URL       : {result.url}")
    print(f"  Analyzed  : {result.analyzed_at}")
    print(f"  Sentences : {result.total_sentences:,} total  |  {len(result.findings)} risky clauses found")
    print("─" * W)

    # ── Risk score ────────────────────────────────────────────────────────────
    sc = _score_color(result.risk_score)
    print(f"\n  {BOLD}OVERALL PRIVACY RISK SCORE{RESET}")
    print(f"\n  {sc}{BOLD}  {result.risk_score} / 100  —  {result.risk_label}  {RESET}\n")
    bar = _score_bar(result.risk_score)
    print(f"  [{sc}{bar}{RESET}]")
    print(f"   0 (Safe){'':>30}100 (Dangerous)")
    print()

    # ── Category summary ──────────────────────────────────────────────────────
    print("─" * W)
    print(f"  {BOLD}FINDINGS BY CATEGORY{RESET}\n")
    for category in RISK_CATEGORIES:
        counts = result.category_counts.get(category.name, {})
        high   = counts.get("high", 0)
        med    = counts.get("medium", 0)
        total  = counts.get("total", 0)

        if total == 0:
            icon  = f"{GREEN}✓{RESET}"
            label = f"{GREEN}Clean{RESET}"
        elif high > 0:
            icon  = f"{RED}✗{RESET}"
            label = f"{RED}{high} HIGH{RESET}"
            if med:
                label += f", {YELLOW}{med} MEDIUM{RESET}"
        else:
            icon  = f"{YELLOW}⚠{RESET}"
            label = f"{YELLOW}{med} MEDIUM{RESET}"

        print(f"  {icon}  {BOLD}{category.name:<40}{RESET}  {label}")

    # ── Detailed findings ─────────────────────────────────────────────────────
    if result.findings:
        print()
        print("─" * W)
        print(f"  {BOLD}DETAILED FLAGGED CLAUSES{RESET}\n")

        for i, finding in enumerate(result.findings, start=1):
            sc2 = _severity_color(finding.severity)
            print(f"  {BOLD}[{i:>2}] {sc2}■ {finding.severity:<8}{RESET}  {CYAN}{finding.category}{RESET}")
            print(f"       {BOLD}Why it's risky:{RESET} {finding.plain_english}")
            print(f"       {WHITE}Clause:{RESET} \"{_truncate(finding.sentence)}\"")
            print()

    # ── GDPR quick check ──────────────────────────────────────────────────────
    print("─" * W)
    print(f"  {BOLD}GDPR COMPLIANCE QUICK CHECK{RESET}\n")

    gdpr_checks = [
        ("Right to Deletion",   "No Right to Deletion"),
        ("No Data Selling",     "Data Selling & Third-Party Sharing"),
        ("Children Protection", "Children's Data Collection"),
        ("Location Consent",    "Location Tracking"),
    ]
    for check_name, category_name in gdpr_checks:
        hits = [f for f in result.findings if f.category == category_name]
        if hits:
            print(f"  {RED}✗  {check_name}: Potential violation detected{RESET}")
        else:
            print(f"  {GREEN}✓  {check_name}: No issues found{RESET}")

    print()
    print("═" * W)
    print(f"  {BOLD}Analysis complete.{RESET}")
    print("═" * W + "\n")


def save_json_report(result: AnalysisResult, filepath: str = "risk_report.json") -> None:
    """
    Exports the full analysis result to a JSON file.

    The JSON file is the contract between the detection engine and
    the Flask backend. The backend reads this file to serve the
    React frontend.

    Args:
        result   -- Completed AnalysisResult from pipeline.run()
        filepath -- Output path (default: risk_report.json)
    """
    data = {
        "url":             result.url,
        "analyzed_at":     result.analyzed_at,
        "total_sentences": result.total_sentences,
        "risk_score":      result.risk_score,
        "risk_label":      result.risk_label,
        "total_findings":  len(result.findings),
        "category_counts": result.category_counts,
        "findings": [
            {
                "sentence":     f.sentence,
                "category":     f.category,
                "severity":     f.severity,
                "plain_english": f.plain_english,
            }
            for f in result.findings
        ]
    }

    with open(filepath, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)

    print(f"[reporter] JSON report saved to: {filepath}")
