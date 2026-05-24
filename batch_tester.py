# week4/batch_tester.py
# ─────────────────────────────────────────────────────────────────────────────
# Week 4 — Batch Policy Tester
#
# Tests the full analysis pipeline against 10 real-world privacy policies and
# produces a comparative evaluation report in both terminal and CSV formats.
#
# This script is the core of the Week 4 evaluation chapter:
#   - Runs every URL through the existing analyzer pipeline
#   - Records risk score, label, finding counts per category
#   - Saves results to evaluation_results.csv for the thesis appendix
#   - Prints a ranked comparison table to the terminal
#
# Note: Meta (Facebook) and Amazon URLs were removed — their pages use
# bot-detection / dynamic rendering that prevents clean text extraction.
# They are still available as Quick Analyze links in the web UI.
#
# Usage:
#   python batch_tester.py               # test all 10 companies
#   python batch_tester.py --limit 3     # test only first 3 (quick test)
#
# ─────────────────────────────────────────────────────────────────────────────

import sys
import csv
import time
import os
import json
from datetime import datetime

# Add parent directory so we can import the analyzer package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from analyzer.pipeline     import run
from analyzer.risk_patterns import RISK_CATEGORIES

# ─────────────────────────────────────────────────────────────────────────────
# TEST SUBJECTS — 10 major companies with their privacy policy URLs
# (Meta/Facebook and Amazon excluded — bot-detection blocks text extraction)
# ─────────────────────────────────────────────────────────────────────────────

TEST_POLICIES = [
    {
        "company": "Google",
        "sector":  "Search / Advertising",
        "url":     "https://policies.google.com/privacy"
    },
    {
        "company": "Apple",
        "sector":  "Consumer Electronics",
        "url":     "https://www.apple.com/legal/privacy/en-ww/"
    },
    {
        "company": "Microsoft",
        "sector":  "Software / Cloud",
        "url":     "https://privacy.microsoft.com/en-us/privacystatement"
    },
    {
        "company": "TikTok",
        "sector":  "Social Media / Video",
        "url":     "https://www.tiktok.com/legal/page/us/privacy-policy/en"
    },
    {
        "company": "Twitter / X",
        "sector":  "Social Media",
        "url":     "https://twitter.com/en/privacy"
    },
    {
        "company": "LinkedIn",
        "sector":  "Professional Network",
        "url":     "https://www.linkedin.com/legal/privacy-policy"
    },
    {
        "company": "Spotify",
        "sector":  "Music Streaming",
        "url":     "https://www.spotify.com/us/legal/privacy-policy/"
    },
    {
        "company": "Airbnb",
        "sector":  "Travel / Marketplace",
        "url":     "https://www.airbnb.com/help/article/2855"
    },
    {
        "company": "Zoom",
        "sector":  "Video Conferencing",
        "url":     "https://explore.zoom.us/en/privacy/"
    },
    {
        "company": "DuckDuckGo",
        "sector":  "Privacy-focused Search",
        "url":     "https://duckduckgo.com/privacy"
    },
]

# ANSI colors
RED    = "\033[91m"
ORANGE = "\033[38;5;208m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

CATEGORY_NAMES = [c.name for c in RISK_CATEGORIES]


def score_color(score):
    if score < 25:  return GREEN
    if score < 50:  return YELLOW
    if score < 75:  return ORANGE
    return RED


def run_batch_test(limit=None):
    """
    Runs the full pipeline on each test URL, collects results,
    prints a terminal report, and saves to CSV + JSON.
    """
    policies = TEST_POLICIES[:limit] if limit else TEST_POLICIES
    results  = []
    failed   = []

    print(f"\n{'=' * 70}")
    print(f"  WEEK 4 — BATCH EVALUATION: {len(policies)} Privacy Policies")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

    for i, policy in enumerate(policies, start=1):
        company = policy['company']
        url     = policy['url']
        print(f"[{i:>2}/{len(policies)}] Analyzing: {BOLD}{company}{RESET}")

        try:
            start  = time.time()
            result = run(
                url,
                print_terminal_report=False,
                save_sentences_to=None,
                save_report_to=None,
            )
            elapsed = round(time.time() - start, 1)

            row = {
                "company":          company,
                "sector":           policy['sector'],
                "url":              url,
                "risk_score":       result.risk_score,
                "risk_label":       result.risk_label,
                "total_sentences":  result.total_sentences,
                "total_findings":   len(result.findings),
                "high_findings":    sum(1 for f in result.findings if f.severity == "HIGH"),
                "medium_findings":  sum(1 for f in result.findings if f.severity == "MEDIUM"),
                "elapsed_sec":      elapsed,
                "analyzed_at":      result.analyzed_at,
            }

            # Add per-category counts
            for cat_name in CATEGORY_NAMES:
                counts = result.category_counts.get(cat_name, {})
                short  = cat_name.split()[0][:8]   # abbreviated for CSV header
                row[f"cat_{short}"] = counts.get("total", 0)

            # Store full findings for JSON export
            row["_findings"] = [
                {"sentence": f.sentence, "category": f.category,
                 "severity": f.severity, "plain_english": f.plain_english}
                for f in result.findings
            ]

            results.append(row)
            sc = score_color(result.risk_score)
            print(f"         Score: {sc}{BOLD}{result.risk_score}/100{RESET} — {result.risk_label} | "
                  f"{len(result.findings)} findings | {elapsed}s\n")

        except Exception as e:
            print(f"         {RED}FAILED: {e}{RESET}\n")
            failed.append({"company": company, "url": url, "error": str(e)})

    # Print ranked comparison table
    _print_comparison_table(results)

    # Save outputs
    _save_csv(results)
    _save_json(results, failed)

    return results, failed


def _print_comparison_table(results):
    """Prints a ranked table sorted by risk score descending."""
    sorted_results = sorted(results, key=lambda r: r['risk_score'], reverse=True)

    print(f"\n{'=' * 70}")
    print(f"  FINAL RANKINGS — Sorted by Risk Score (Highest = Most Dangerous)")
    print(f"{'=' * 70}")
    print(f"\n  {'#':<3} {'Company':<20} {'Score':>6} {'Label':<16} {'Findings':>8} {'HIGH':>5} {'MED':>5}")
    print(f"  {'─' * 65}")

    for rank, r in enumerate(sorted_results, start=1):
        sc    = score_color(r['risk_score'])
        label = r['risk_label']
        print(f"  {rank:<3} {r['company']:<20} "
              f"{sc}{r['risk_score']:>5}/100{RESET}  "
              f"{label:<16} "
              f"{r['total_findings']:>8}  "
              f"{RED}{r['high_findings']:>4}{RESET}  "
              f"{YELLOW}{r['medium_findings']:>4}{RESET}")

    print(f"\n  {'─' * 65}")

    # Summary stats
    scores = [r['risk_score'] for r in results]
    print(f"\n  Average score : {sum(scores)/len(scores):.1f}/100")
    print(f"  Highest score : {max(scores)}/100 ({next(r['company'] for r in results if r['risk_score']==max(scores))})")
    print(f"  Lowest score  : {min(scores)}/100 ({next(r['company'] for r in results if r['risk_score']==min(scores))})")
    print(f"\n{'=' * 70}\n")


def _save_csv(results):
    """Saves evaluation results to CSV (for thesis appendix)."""
    if not results:
        return

    filepath = os.path.join(os.path.dirname(__file__), "evaluation_results.csv")
    # Exclude internal _findings key from CSV
    fieldnames = [k for k in results[0].keys() if not k.startswith("_")]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({k: v for k, v in row.items() if not k.startswith("_")})

    print(f"[+] CSV saved to: {filepath}")


def _save_json(results, failed):
    """Saves full results including findings to JSON."""
    filepath = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tested":  len(results),
        "total_failed":  len(failed),
        "results": results,
        "failed":  failed,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[+] JSON saved to: {filepath}\n")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        try:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        except (IndexError, ValueError):
            pass

    run_batch_test(limit=limit)
