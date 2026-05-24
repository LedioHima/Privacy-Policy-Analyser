"""
Compatibility shim.

The real pipeline lives in `analyzer/pipeline.py`.
This file exists to avoid breaking older imports like `import pipeline`.
"""

from analyzer.pipeline import run, run_from_text  # noqa: F401

__all__ = ["run", "run_from_text"]
