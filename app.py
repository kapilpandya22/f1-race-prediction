import os
import json
import csv
import subprocess
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboards')   # HTML + video live here
VENV_PYTHON   = os.path.join(BASE_DIR, '.venv', 'Scripts', 'python.exe')

F1_2026_SCHEDULE = [
    {"race": "Australian Grand Prix",       "quali_end": "2026-03-07T07:00", "race_end": "2026-03-08T08:00"},
    {"race": "Chinese Grand Prix",          "quali_end": "2026-03-14T09:00", "race_end": "2026-03-15T11:00"},
    {"race": "Japanese Grand Prix",         "quali_end": "2026-03-28T08:00", "race_end": "2026-03-29T10:00"},
    {"race": "Miami Grand Prix",            "quali_end": "2026-05-02T23:00", "race_end": "2026-05-03T22:00"},
    {"race": "Canadian Grand Prix",         "quali_end": "2026-05-23T23:00", "race_end": "2026-05-25T01:00"},
    {"race": "Monaco Grand Prix",           "quali_end": "2026-06-06T17:00", "race_end": "2026-06-07T18:00"},
    {"race": "Barcelona-Catalunya GP",      "quali_end": "2026-06-13T17:00", "race_end": "2026-06-14T18:00"},
    {"race": "Austrian Grand Prix",         "quali_end": "2026-06-27T17:00", "race_end": "2026-06-28T18:00"},
    {"race": "British Grand Prix",          "quali_end": "2026-07-04T18:00", "race_end": "2026-07-05T19:00"},
    {"race": "Belgian Grand Prix",          "quali_end": "2026-07-18T17:00", "race_end": "2026-07-19T18:00"},
    {"race": "Hungarian Grand Prix",        "quali_end": "2026-07-25T17:00", "race_end": "2026-07-26T18:00"},
    {"race": "Dutch Grand Prix",            "quali_end": "2026-08-22T17:00", "race_end": "2026-08-23T18:00"},
    {"race": "Italian Grand Prix",          "quali_end": "2026-09-05T17:00", "race_end": "2026-09-06T18:00"},
    {"race": "Spanish Grand Prix (Madrid)", "quali_end": "2026-09-12T17:00", "race_end": "2026-09-13T18:00"},
    {"race": "Azerbaijan Grand Prix",       "quali_end": "2026-09-25T15:00", "race_end": "2026-09-26T16:00"},
    {"race": "Singapore Grand Prix",        "quali_end": "2026-10-10T16:00", "race_end": "2026-10-11T17:00"},
    {"race": "United States Grand Prix",    "quali_end": "2026-10-25T00:00", "race_end": "2026-10-26T00:00"},
    {"race": "Mexico City Grand Prix",      "quali_end": "2026-10-31T23:00", "race_end": "2026-11-02T00:00"},
    {"race": "Brazilian Grand Prix",        "quali_end": "2026-11-07T20:00", "race_end": "2026-11-08T21:00"},
    {"race": "Las Vegas Grand Prix",        "quali_end": "2026-11-21T06:00", "race_end": "2026-11-22T08:00"},
    {"race": "Qatar Grand Prix",            "quali_end": "2026-11-28T20:00", "race_end": "2026-11-29T20:00"},
    {"race": "Abu Dhabi Grand Prix",        "quali_end": "2026-12-05T16:00", "race_end": "2026-12-06T17:00"},
]

# ── HELPERS ──────────────────────────────────────────────────────────────────

def berlin_offset(month):
    return 2 if 4 <= month <= 10 else 1

def parse_berlin_to_utc(dt_str):
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
    return (dt - timedelta(hours=berlin_offset(dt.month))).replace(tzinfo=timezone.utc)

def race_folder_name(race_name):
    return f"2026_{race_name.replace(' ', '_')}"

def predictions_path(model, race):
    return os.path.join(BASE_DIR, 'outputs', 'predictions', model,
                        race_folder_name(race), 'predictions.csv')

def metrics_path(model, race):
    return os.path.join(BASE_DIR, 'outputs', 'predictions', model,
                        race_folder_name(race), 'metrics.json')

def has_real_metrics(model, race):
    p = metrics_path(model, race)
    if not os.path.exists(p):
        return False
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return bool(json.load(f).get('has_ground_truth', False))
    except Exception:
        return False

def compute_status(race_name, model_name):
    entry = next((r for r in F1_2026_SCHEDULE if r['race'] == race_name), None)
    if not entry:
        return 'NOT_READY'
    now       = datetime.now(timezone.utc)
    quali_end = parse_berlin_to_utc(entry['quali_end'])
    race_end  = parse_berlin_to_utc(entry['race_end'])
    has_preds = os.path.exists(predictions_path(model_name, race_name))
    has_met   = has_real_metrics(model_name, race_name)

    if now < quali_end:             return 'NOT_READY'
    if not has_preds:               return 'NOT_READY'
    if now >= race_end and has_met: return 'COMPLETED'
    return 'PREDICTION'

def csv_to_list(filepath):
    if not os.path.exists(filepath):
        return []
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows

def run_subprocess(cmd, cwd, timeout):
    """Run subprocess with UTF-8 encoding. Returns (success, stdout, stderr, elapsed)."""
    t_start = datetime.now(timezone.utc)
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True,
            capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
        )
        elapsed = int((datetime.now(timezone.utc) - t_start).total_seconds())
        if result.stdout and result.stdout.strip():
            print(f"\n[OK] {cmd[-1]} stdout:\n{result.stdout[-500:]}", flush=True)
        if result.stderr and result.stderr.strip():
            print(f"\n[OK] {cmd[-1]} stderr:\n{result.stderr[-500:]}", flush=True)
        return True, result.stdout, result.stderr, elapsed

    except subprocess.CalledProcessError as e:
        elapsed = int((datetime.now(timezone.utc) - t_start).total_seconds())
        print(f"\n[ERROR] {cmd[-1]}", flush=True)
        print(f"  STDOUT: {e.stdout[-800:] if e.stdout else 'none'}", flush=True)
        print(f"  STDERR: {e.stderr[-800:] if e.stderr else 'none'}", flush=True)
        err_msg = e.stderr[-600:] if e.stderr else (e.stdout[-600:] if e.stdout else 'Process failed with no output')
        return False, e.stdout or '', err_msg, elapsed

    except subprocess.TimeoutExpired:
        elapsed = int((datetime.now(timezone.utc) - t_start).total_seconds())
        print(f"\n[TIMEOUT] {cmd[-1]} after {timeout}s", flush=True)
        return False, '', f'Pipeline timed out after {timeout} seconds', elapsed

# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file(os.path.join(DASHBOARD_DIR, 'f1_step1_v9.html'))

@app.route('/dashboard')
def dashboard():
    return send_file(os.path.join(DASHBOARD_DIR, 'f1_dashboard_p2.html'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(os.path.join(DASHBOARD_DIR, filename))

@app.route('/f1_bg.mp4')
def serve_video():
    video_path = os.path.join(DASHBOARD_DIR, 'f1_bg.mp4')
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found in dashboards/'}), 404
    return send_file(video_path, mimetype='video/mp4', conditional=True)

@app.route('/api/health')
def health():
    return jsonify({
        'status':        'ok',
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'base_dir':      BASE_DIR,
        'dashboard_dir': DASHBOARD_DIR,
        'venv_exists':   os.path.exists(VENV_PYTHON),
        'dash_exists':   os.path.exists(DASHBOARD_DIR),
    })

@app.route('/api/races/status')
def races_status():
    model = request.args.get('model', 'random_forest')
    result = []
    for entry in F1_2026_SCHEDULE:
        rn     = entry['race']
        status = compute_status(rn, model)
        result.append({
            'race':            rn,
            'status':          status,
            'has_predictions': os.path.exists(predictions_path(model, rn)),
            'has_metrics':     has_real_metrics(model, rn),
            'quali_end':       entry['quali_end'],
            'race_end':        entry['race_end'],
        })
    return jsonify(result)

@app.route('/api/data')
def api_data():
    model = request.args.get('model', 'random_forest')
    race  = request.args.get('race', '')
    if not race:
        return jsonify({'error': 'race parameter required'}), 400

    folder = os.path.join(BASE_DIR, 'outputs', 'predictions', model, race_folder_name(race))
    if not os.path.exists(folder):
        return jsonify({'error': f'No data for {race} ({model})'}), 404

    preds = csv_to_list(os.path.join(folder, 'predictions.csv'))
    if not preds:
        return jsonify({'error': f'predictions.csv missing for {race} ({model})'}), 404

    result = {
        'predictions':         preds,
        'feature_importance':  csv_to_list(os.path.join(folder, 'feature_importance.csv')),
        'driver_explanations': csv_to_list(os.path.join(folder, 'driver_explanations.csv')),
        'metrics': {},
    }
    mp = os.path.join(folder, 'metrics.json')
    if os.path.exists(mp):
        with open(mp, 'r', encoding='utf-8') as f:
            result['metrics'] = json.load(f)

    return jsonify(result)

@app.route('/api/update', methods=['POST'])
def api_update():
    body  = request.get_json() or {}
    model = body.get('model', 'random_forest')

    print(f"\n{'='*60}", flush=True)
    print(f"[UPDATE] Starting update for model: {model}", flush=True)
    print(f"{'='*60}", flush=True)

    def generate():
        now = datetime.now(timezone.utc)

        for entry in F1_2026_SCHEDULE:
            rn        = entry['race']
            quali_end = parse_berlin_to_utc(entry['quali_end'])
            race_end  = parse_berlin_to_utc(entry['race_end'])

            if now < quali_end:
                continue

            has_preds = os.path.exists(predictions_path(model, rn))

            # ── PREDICTIONS ──────────────────────────────────────────
            if not has_preds:
                print(f"\n[UPDATE] Running prediction for: {rn}", flush=True)
                yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"running"})}\n\n'

                ok, stdout, stderr, elapsed = run_subprocess(
                    [VENV_PYTHON, '-m', 'pipelines.run_prediction', rn],
                    BASE_DIR, 600
                )

                if not ok:
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"error","msg":stderr[-400:],"elapsed":elapsed})}\n\n'
                    continue

                if os.path.exists(predictions_path(model, rn)):
                    print(f"[UPDATE] ✓ Predictions verified for: {rn}", flush=True)
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"done","elapsed":elapsed})}\n\n'
                else:
                    msg = f'Pipeline ran ({elapsed}s) but predictions.csv not found. stdout: {stdout[-300:]}'
                    print(f"[UPDATE] ✗ No output file for: {rn}", flush=True)
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"error","msg":msg,"elapsed":elapsed})}\n\n'
                    continue
            else:
                print(f"[UPDATE] Skipping {rn} — predictions already exist", flush=True)
                yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"already_done"})}\n\n'

            # ── METRICS (only if race has finished) ──────────────────
            if now >= race_end and not has_real_metrics(model, rn):
                print(f"\n[UPDATE] Running metrics for: {rn}", flush=True)
                yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"running"})}\n\n'

                ok, stdout, stderr, elapsed = run_subprocess(
                    [VENV_PYTHON, '-m', 'pipelines.run_metrics', rn],
                    BASE_DIR, 300
                )

                if not ok:
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"error","msg":stderr[-400:],"elapsed":elapsed})}\n\n'
                elif has_real_metrics(model, rn):
                    print(f"[UPDATE] ✓ Metrics verified for: {rn}", flush=True)
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"done","elapsed":elapsed})}\n\n'
                else:
                    msg = f'Metrics ran ({elapsed}s) but has_ground_truth=false or metrics.json missing'
                    print(f"[UPDATE] ✗ Metrics incomplete for: {rn}", flush=True)
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"error","msg":msg,"elapsed":elapsed})}\n\n'

        print(f"\n[UPDATE] All done!", flush=True)
        yield f'data: {json.dumps({"type":"done","message":"All races updated"})}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )

@app.route('/api/run/metrics', methods=['POST'])
def run_metrics_endpoint():
    data = request.get_json() or {}
    race = data.get('race', '')
    if not race:
        return jsonify({'error': 'race required'}), 400

    print(f"\n[METRICS] Running metrics for: {race}", flush=True)
    ok, stdout, stderr, elapsed = run_subprocess(
        [VENV_PYTHON, '-m', 'pipelines.run_metrics', race],
        BASE_DIR, 300
    )
    if ok:
        return jsonify({'status': 'ok', 'race': race, 'elapsed': elapsed})
    else:
        return jsonify({'error': stderr[:500], 'elapsed': elapsed}), 500

if __name__ == '__main__':
    print(f"\n{'='*60}", flush=True)
    print(f"  F1 Race Prediction — Dashboard Server", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"  BASE_DIR      : {BASE_DIR}", flush=True)
    print(f"  DASHBOARD_DIR : {DASHBOARD_DIR}", flush=True)
    print(f"  VENV_PYTHON   : {VENV_PYTHON}", flush=True)
    print(f"  Venv exists   : {os.path.exists(VENV_PYTHON)}", flush=True)
    print(f"  Dashboards    : {os.path.exists(DASHBOARD_DIR)}", flush=True)
    print(f"  Landing page  : {os.path.exists(os.path.join(DASHBOARD_DIR, 'f1_step1_v9.html'))}", flush=True)
    print(f"  Dashboard p2  : {os.path.exists(os.path.join(DASHBOARD_DIR, 'f1_dashboard_p2.html'))}", flush=True)
    print(f"  Video         : {os.path.exists(os.path.join(DASHBOARD_DIR, 'f1_bg.mp4'))}", flush=True)
    print(f"{'='*60}\n", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)