# analyzer/pipeline.py  (Week 3 update — adds run_from_text)
# ─────────────────────────────────────────────────────────────────────────────
# Orchestrates all pipeline stages. Two entry points:
#   run()            → full pipeline from a URL (or sentences file)
#   run_from_text()  → pipeline starting from raw pasted text (no fetching)
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime

from .models import AnalysisResult
from .fetcher import fetch_html, clean_html
from .splitter import split_sentences, sentences_from_file, save_sentences
from .detector import detect_risks, summarize_by_category
from .scorer import calculate_risk_score
from .reporter import print_report, save_json_report


def run(
    source: str,
    from_file: bool = False,
    save_sentences_to: str | None = "policy_sentences.txt",
    save_report_to: str | None = "risk_report.json",
    print_terminal_report: bool = True,
) -> AnalysisResult:
    """
    Full pipeline from a URL or saved sentences file.

    Args:
        source                -- URL or path to a sentences file
        from_file             -- If True, treat source as a file path
        save_sentences_to     -- Save extracted sentences here (None = skip)
        save_report_to        -- Save JSON report here (None = skip)
        print_terminal_report -- Print color-coded report to terminal

    Returns:
        Completed AnalysisResult
    """
    _banner("Privacy Policy Analyzer — Full Pipeline")

    if from_file:
        sentences = sentences_from_file(source)
        url_label = source
    else:
        html = fetch_html(source)
        text = clean_html(html)
        sentences = split_sentences(text)
        url_label = source

        if save_sentences_to:
            save_sentences(sentences, save_sentences_to)

    return _run_analysis(sentences, url_label, save_report_to, print_terminal_report)


def run_from_text(
    text: str,
    label: str = "Pasted Policy Text",
    save_report_to: str | None = None,
    print_terminal_report: bool = False,
) -> AnalysisResult:
    """
    Pipeline starting from raw pasted text — skips fetching entirely.
    Used by the /api/analyze/text endpoint.

    Args:
        text                  -- Raw privacy policy text pasted by the user
        label                 -- Display name for this policy in the report
        save_report_to        -- Save JSON report here (None = skip)
        print_terminal_report -- Print color-coded report to terminal

    Returns:
        Completed AnalysisResult
    """
    _banner("Privacy Policy Analyzer — Text Input Pipeline")

    import re

    normalized = re.sub(r"\s+", " ", text).strip()
    sentences = split_sentences(normalized)

    return _run_analysis(sentences, label, save_report_to, print_terminal_report)


# ── Shared analysis stages (used by both entry points) ───────────────────────


def _run_analysis(
    sentences: list[str],
    url_label: str,
    save_report_to: str | None,
    print_terminal_report: bool,
) -> AnalysisResult:
    print(f"[pipeline] Scanning {len(sentences):,} sentences across 7 risk categories...")
    findings = detect_risks(sentences)
    print(f"[pipeline] Found {len(findings)} risky clauses")

    risk_score, risk_label = calculate_risk_score(findings, len(sentences))
    print(f"[pipeline] Risk score: {risk_score}/100 — {risk_label}")

    result = AnalysisResult(
        url=url_label,
        total_sentences=len(sentences),
        findings=findings,
        risk_score=risk_score,
        risk_label=risk_label,
        category_counts=summarize_by_category(findings),
        analyzed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    if print_terminal_report:
        print_report(result)

    if save_report_to:
        save_json_report(result, save_report_to)

    return result


def _banner(title: str) -> None:
    print(f"\n{'=' * 70}\n  {title}\n{'=' * 70}\n")

