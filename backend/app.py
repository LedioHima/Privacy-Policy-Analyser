# backend/app.py
# ─────────────────────────────────────────────────────────────────────────────
# Privacy Policy Analyzer — Flask REST API (Week 3)
#
# Endpoints:
#   POST   /api/analyze         → Analyze a URL, returns full AnalysisResult JSON
#   POST   /api/analyze/text    → Analyze pasted raw text
#   GET    /api/history         → List recently analyzed policies (from SQLite cache)
#   DELETE /api/history         → Body: { "ids": [1,2,3] } — remove multiple rows
#   GET    /api/result/<id>     → Fetch a cached result by ID
#   DELETE /api/result/<id>     → Remove one cached result
#   GET    /api/health          → Health check
#
# Install:
#   pip install flask flask-cors
# Run:
#   python app.py
# ─────────────────────────────────────────────────────────────────────────────

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory to path so we can import the analyzer package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from analyzer.pipeline import run, run_from_text
from analyzer.models import AnalysisResult

# Support both:
# - `python backend/app.py` (imports cache as a local module)
# - `python -m backend.app` / `import backend.app` (package-relative import)
try:
    from .cache import (  # type: ignore
        init_db,
        save_result,
        get_result,
        list_results,
        delete_result_by_id,
        delete_results_by_ids,
    )
except ImportError:  # pragma: no cover
    from cache import (
        init_db,
        save_result,
        get_result,
        list_results,
        delete_result_by_id,
        delete_results_by_ids,
    )

app = Flask(__name__)
CORS(app)   # Allow React frontend (localhost:5173) to call this API

# ── Initialize SQLite cache on startup ───────────────────────────────────────
init_db()


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/analyze
# Body: { "url": "https://policies.google.com/privacy" }
# Returns: full AnalysisResult as JSON
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({ 'error': 'Missing required field: url' }), 400

    url = data['url'].strip()
    if not url.startswith(('http://', 'https://')):
        return jsonify({ 'error': 'URL must start with http:// or https://' }), 400

    # Check cache first — avoid re-analyzing the same URL
    cached = get_result(url=url)
    if cached:
        return jsonify({ 'cached': True, **cached })

    try:
        result = run(url, print_terminal_report=False, save_sentences_to=None, save_report_to=None)
        result_dict = _result_to_dict(result)
        save_result(result_dict)
        return jsonify({ 'cached': False, **result_dict })

    except Exception as e:
        return jsonify({ 'error': str(e) }), 500


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/analyze/text
# Body: { "text": "<full policy text>", "label": "My Company Policy" }
# Returns: full AnalysisResult as JSON
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({ 'error': 'Missing required field: text' }), 400

    text  = data['text'].strip()
    label = data.get('label', 'Pasted Policy Text')

    if len(text) < 100:
        return jsonify({ 'error': 'Text is too short to be a valid privacy policy' }), 400

    try:
        result = run_from_text(text, label=label, print_terminal_report=False, save_report_to=None)
        result_dict = _result_to_dict(result)
        save_result(result_dict)
        return jsonify({ 'cached': False, **result_dict })

    except Exception as e:
        return jsonify({ 'error': str(e) }), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/history    — list of the 10 most recently analyzed policies
# DELETE /api/history — body: { "ids": [1, 2, 3] }
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/api/history', methods=['GET', 'DELETE'])
def history():
    if request.method == 'DELETE':
        data = request.get_json() or {}
        ids = data.get('ids')
        if not isinstance(ids, list) or not ids:
            return jsonify({ 'error': 'Body must include a non-empty ids array' }), 400
        try:
            id_list = [int(x) for x in ids]
        except (TypeError, ValueError):
            return jsonify({ 'error': 'Each id must be an integer' }), 400
        deleted = delete_results_by_ids(id_list)
        return jsonify({ 'ok': True, 'deleted_count': deleted })

    results = list_results(limit=10)
    return jsonify(results)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/result/<result_id>    — full cached AnalysisResult
# DELETE /api/result/<result_id> — remove one row
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/api/result/<int:result_id>', methods=['GET', 'DELETE'])
def cached_result(result_id):
    if request.method == 'DELETE':
        if delete_result_by_id(result_id):
            return jsonify({ 'ok': True, 'deleted': result_id })
        return jsonify({ 'error': 'Result not found' }), 404

    result = get_result(result_id=result_id)
    if not result:
        return jsonify({ 'error': 'Result not found' }), 404
    return jsonify(result)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/health
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({ 'status': 'ok', 'version': '3.0.0' })


# ─────────────────────────────────────────────────────────────────────────────
# Helper — convert AnalysisResult dataclass → plain dict for JSON serialization
# ─────────────────────────────────────────────────────────────────────────────
def _result_to_dict(result: AnalysisResult) -> dict:
    return {
        'url':             result.url,
        'analyzed_at':     result.analyzed_at,
        'total_sentences': result.total_sentences,
        'risk_score':      result.risk_score,
        'risk_label':      result.risk_label,
        'total_findings':  len(result.findings),
        'category_counts': result.category_counts,
        'findings': [
            {
                'sentence':      f.sentence,
                'category':      f.category,
                'severity':      f.severity,
                'plain_english': f.plain_english,
            }
            for f in result.findings
        ]
    }


if __name__ == '__main__':
    print("\n  Privacy Policy Analyzer — Flask API")
    print("  Running at: http://localhost:5000\n")
    app.run(debug=True, port=5000)
