# analyzer/splitter.py
# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 of the pipeline: Split
#
# Responsibilities:
#   - Load spaCy's English NLP model
#   - Split a long plain-text string into a list of individual sentences
#   - Filter out very short fragments (navigation leftovers, page numbers, etc.)
#
# Why spaCy instead of splitting on "."?
#   Privacy policies are full of abbreviations ("U.S.", "Inc.", "No. 5")
#   and numbered clauses ("3.1. You agree...") that would cause naive period-
#   splitting to produce garbage sentences. spaCy's trained model handles all
#   of these correctly.
# ─────────────────────────────────────────────────────────────────────────────

import spacy

# Any sentence shorter than this (in characters) is considered a fragment
# and discarded (e.g. "1.", "Back", "Top")
_MIN_SENTENCE_LENGTH = 20

# spaCy's default max is 1 000 000 chars; we set it explicitly to be safe
_MAX_NLP_CHARS = 1_000_000


def load_nlp_model(model_name: str = "en_core_web_sm"):
    """
    Loads and returns a spaCy language model.
    Call this once and reuse the result — loading is expensive.

    Args:
        model_name -- spaCy model identifier (default: en_core_web_sm)

    Returns:
        A spaCy Language object

    Raises:
        OSError -- If the model hasn't been downloaded yet.
                   Fix: python -m spacy download en_core_web_sm
    """
    print(f"[splitter] Loading spaCy model '{model_name}'...")
    nlp = spacy.load(model_name)
    nlp.max_length = _MAX_NLP_CHARS
    return nlp


def split_sentences(text: str, nlp=None) -> list[str]:
    """
    Splits plain text into a list of individual sentences using spaCy.

    Args:
        text -- Cleaned plain-text string from fetcher.clean_html()
        nlp  -- Optional pre-loaded spaCy model. If None, loads automatically.
                Pass a pre-loaded model when calling this function multiple
                times to avoid reloading the model on each call.

    Returns:
        List of sentence strings, filtered to remove short fragments.
    """
    if nlp is None:
        nlp = load_nlp_model()

    # Truncate if longer than the model's limit
    doc = nlp(text[:_MAX_NLP_CHARS])

    sentences = [
        sent.text.strip()
        for sent in doc.sents
        if len(sent.text.strip()) >= _MIN_SENTENCE_LENGTH
    ]

    print(f"[splitter] Split into {len(sentences):,} sentences")
    return sentences


def sentences_from_file(filepath: str) -> list[str]:
    """
    Loads a pre-saved sentences file produced by save_sentences().
    Useful for re-running the detection stage without re-fetching the URL.

    Args:
        filepath -- Path to a plain-text file with one sentence per line

    Returns:
        List of sentence strings
    """
    print(f"[splitter] Reading sentences from file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        sentences = [
            line.strip()
            for line in f
            if len(line.strip()) >= _MIN_SENTENCE_LENGTH
        ]
    print(f"[splitter] Loaded {len(sentences):,} sentences")
    return sentences


def save_sentences(sentences: list[str], filepath: str = "policy_sentences.txt"):
    """
    Saves the sentence list to a plain-text file (one sentence per line).
    The file can later be reloaded with sentences_from_file().

    Args:
        sentences -- List of sentence strings
        filepath  -- Output file path (default: policy_sentences.txt)
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for sentence in sentences:
            f.write(sentence + "\n")
    print(f"[splitter] Saved {len(sentences):,} sentences to: {filepath}")
