#!/usr/bin/env python3
"""
Privacy Policy Analyzer — Command Line Entry Point
====================================================
Run the full analysis pipeline from the terminal.

Usage:
    # Analyze a live URL (default: Google Privacy Policy)
    python main.py

    # Analyze any URL
    python main.py https://policies.google.com/privacy
    python main.py https://www.facebook.com/privacy/policy/
    python main.py https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ

    # Analyze from a saved sentences file (skips re-fetching)
    python main.py --file policy_sentences.txt

Output:
    - Color-coded report printed to terminal
    - policy_sentences.txt  — extracted sentences (reuse with --file)
    - risk_report.json      — full results for the Flask backend
"""

import sys
from analyzer.pipeline import run

DEFAULT_URL = "https://policies.google.com/privacy"


def main():
    args = sys.argv[1:]

    if not args:
        # No arguments — analyze the default URL
        run(DEFAULT_URL)

    elif len(args) == 1:
        # Single argument — treat as a URL
        run(args[0])

    elif len(args) == 2 and args[0] == "--file":
        # --file <path> — read from saved sentences file
        run(args[1], from_file=True)

    else:
        print("Usage:")
        print("  python main.py                              # default (Google)")
        print("  python main.py <url>                        # any URL")
        print("  python main.py --file policy_sentences.txt  # from saved file")
        sys.exit(1)


if __name__ == "__main__":
    main()
