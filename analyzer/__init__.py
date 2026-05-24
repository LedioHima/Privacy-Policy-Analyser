# privacy_analyzer/__init__.py
# Makes this folder a proper Python package.
# Import the top-level run() function so callers can do:
#   from privacy_analyzer import run
#   run("https://policies.google.com/privacy")

from .pipeline import run

__all__ = ["run"]
