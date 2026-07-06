import os
import json
import csv
import glob
import subprocess
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR      = os.path.join(BASE_DIR, 'dashboards')
VENV_PYTHON        = 'python'
GOLDEN_DIR         = os.path.join(BASE_DIR, 'data', 'golden')
GOLDEN_DASH_DIR    = os.path.join(BASE_DIR, 'data', 'golden', 'dashboard')

# ── 2026 RACE SCHEDULE ───────────────────────────────────────────────────────
# quali_end / race_end are Berlin (CET/CEST) local times.
# race_start is UTC.

F1_2026_SCHEDULE = [
    {"race": "Australian Grand Prix",    "round": 1,  "quali_end": "2026-03-07T07:00", "race_end": "2026-03-08T08:00",  "race_start_utc": "2026-03-08T06:00:00Z", "race_date_display": "March 8, 2026"},
    {"race": "Chinese Grand Prix",       "round": 2,  "quali_end": "2026-03-14T09:00", "race_end": "2026-03-15T11:00",  "race_start_utc": "2026-03-15T07:00:00Z", "race_date_display": "March 15, 2026"},
    {"race": "Japanese Grand Prix",      "round": 3,  "quali_end": "2026-03-28T08:00", "race_end": "2026-03-29T10:00",  "race_start_utc": "2026-03-29T05:00:00Z", "race_date_display": "March 29, 2026"},
    {"race": "Miami Grand Prix",         "round": 4,  "quali_end": "2026-05-02T23:00", "race_end": "2026-05-03T22:00",  "race_start_utc": "2026-05-03T20:00:00Z", "race_date_display": "May 3, 2026"},
    {"race": "Canadian Grand Prix",      "round": 5,  "quali_end": "2026-05-23T23:00", "race_end": "2026-05-25T01:00",  "race_start_utc": "2026-05-24T18:00:00Z", "race_date_display": "May 24, 2026"},
    {"race": "Monaco Grand Prix",        "round": 6,  "quali_end": "2026-06-06T17:00", "race_end": "2026-06-07T18:00",  "race_start_utc": "2026-06-07T13:00:00Z", "race_date_display": "June 7, 2026"},
    {"race": "Barcelona Grand Prix",     "round": 7,  "quali_end": "2026-06-13T17:00", "race_end": "2026-06-14T18:00",  "race_start_utc": "2026-06-14T13:00:00Z", "race_date_display": "June 14, 2026"},
    {"race": "Austrian Grand Prix",      "round": 8,  "quali_end": "2026-06-27T17:00", "race_end": "2026-06-28T18:00",  "race_start_utc": "2026-06-28T13:00:00Z", "race_date_display": "June 28, 2026"},
    {"race": "British Grand Prix",       "round": 9,  "quali_end": "2026-07-04T18:00", "race_end": "2026-07-05T19:00",  "race_start_utc": "2026-07-05T14:00:00Z", "race_date_display": "July 5, 2026"},
    {"race": "Belgian Grand Prix",       "round": 10, "quali_end": "2026-07-18T17:00", "race_end": "2026-07-19T18:00",  "race_start_utc": "2026-07-19T13:00:00Z", "race_date_display": "July 19, 2026"},
    {"race": "Hungarian Grand Prix",     "round": 11, "quali_end": "2026-07-25T17:00", "race_end": "2026-07-26T18:00",  "race_start_utc": "2026-07-26T13:00:00Z", "race_date_display": "July 26, 2026"},
    {"race": "Dutch Grand Prix",         "round": 12, "quali_end": "2026-08-22T17:00", "race_end": "2026-08-23T18:00",  "race_start_utc": "2026-08-23T13:00:00Z", "race_date_display": "August 23, 2026"},
    {"race": "Italian Grand Prix",       "round": 13, "quali_end": "2026-09-05T17:00", "race_end": "2026-09-06T18:00",  "race_start_utc": "2026-09-06T13:00:00Z", "race_date_display": "September 6, 2026"},
    {"race": "Spanish Grand Prix",       "round": 14, "quali_end": "2026-09-12T17:00", "race_end": "2026-09-13T18:00",  "race_start_utc": "2026-09-13T13:00:00Z", "race_date_display": "September 13, 2026"},
    {"race": "Azerbaijan Grand Prix",    "round": 15, "quali_end": "2026-09-25T15:00", "race_end": "2026-09-26T16:00",  "race_start_utc": "2026-09-26T11:00:00Z", "race_date_display": "September 26, 2026"},
    {"race": "Singapore Grand Prix",     "round": 16, "quali_end": "2026-10-10T16:00", "race_end": "2026-10-11T17:00",  "race_start_utc": "2026-10-11T12:00:00Z", "race_date_display": "October 11, 2026"},
    {"race": "United States Grand Prix", "round": 17, "quali_end": "2026-10-25T00:00", "race_end": "2026-10-26T00:00",  "race_start_utc": "2026-10-25T19:00:00Z", "race_date_display": "October 25, 2026"},
    {"race": "Mexico City Grand Prix",   "round": 18, "quali_end": "2026-10-31T23:00", "race_end": "2026-11-02T00:00",  "race_start_utc": "2026-11-01T20:00:00Z", "race_date_display": "November 1, 2026"},
    {"race": "São Paulo Grand Prix",     "round": 19, "quali_end": "2026-11-07T20:00", "race_end": "2026-11-08T21:00",  "race_start_utc": "2026-11-08T17:00:00Z", "race_date_display": "November 8, 2026"},
    {"race": "Las Vegas Grand Prix",     "round": 20, "quali_end": "2026-11-21T06:00", "race_end": "2026-11-22T08:00",  "race_start_utc": "2026-11-22T06:00:00Z", "race_date_display": "November 22, 2026"},
    {"race": "Qatar Grand Prix",         "round": 21, "quali_end": "2026-11-28T20:00", "race_end": "2026-11-29T20:00",  "race_start_utc": "2026-11-29T17:00:00Z", "race_date_display": "November 29, 2026"},
    {"race": "Abu Dhabi Grand Prix",     "round": 22, "quali_end": "2026-12-05T16:00", "race_end": "2026-12-06T17:00",  "race_start_utc": "2026-12-06T13:00:00Z", "race_date_display": "December 6, 2026"},
]

# ── DRS ZONES & LAP RECORDS ──────────────────────────────────────────────────
DRS_AND_RECORDS = {
    'Australian Grand Prix':    {'drs_zones': 4, 'lap_record': '1:20.235'},
    'Chinese Grand Prix':       {'drs_zones': 2, 'lap_record': '1:32.238'},
    'Japanese Grand Prix':      {'drs_zones': 1, 'lap_record': '1:30.983'},
    'Miami Grand Prix':         {'drs_zones': 3, 'lap_record': '1:29.708'},
    'Canadian Grand Prix':      {'drs_zones': 2, 'lap_record': '1:13.078'},
    'Monaco Grand Prix':        {'drs_zones': 1, 'lap_record': '1:12.909'},
    'Barcelona Grand Prix':     {'drs_zones': 2, 'lap_record': '1:16.330'},
    'Spanish Grand Prix':       {'drs_zones': 2, 'lap_record': '1:16.330'},
    'Austrian Grand Prix':      {'drs_zones': 3, 'lap_record': '1:05.619'},
    'British Grand Prix':       {'drs_zones': 2, 'lap_record': '1:27.097'},
    'Belgian Grand Prix':       {'drs_zones': 2, 'lap_record': '1:46.286'},
    'Hungarian Grand Prix':     {'drs_zones': 2, 'lap_record': '1:16.627'},
    'Dutch Grand Prix':         {'drs_zones': 2, 'lap_record': '1:11.097'},
    'Italian Grand Prix':       {'drs_zones': 2, 'lap_record': '1:21.046'},
    'Spanish Grand Prix (Madrid)': {'drs_zones': 3, 'lap_record': 'N/A'},
    'Azerbaijan Grand Prix':    {'drs_zones': 2, 'lap_record': '1:43.009'},
    'Singapore Grand Prix':     {'drs_zones': 3, 'lap_record': '1:35.867'},
    'United States Grand Prix': {'drs_zones': 3, 'lap_record': '1:36.169'},
    'Mexico City Grand Prix':   {'drs_zones': 2, 'lap_record': '1:17.774'},
    'São Paulo Grand Prix':     {'drs_zones': 2, 'lap_record': '1:10.540'},
    'Las Vegas Grand Prix':     {'drs_zones': 3, 'lap_record': '1:35.490'},
    'Qatar Grand Prix':         {'drs_zones': 3, 'lap_record': '1:24.319'},
    'Abu Dhabi Grand Prix':     {'drs_zones': 2, 'lap_record': '1:26.103'},
    'Emilia Romagna Grand Prix': {'drs_zones': 2, 'lap_record': '1:15.484'},
}

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
    return os.path.join(BASE_DIR, 'outputs', 'analysis', model,
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

def safe_float(v, default=0.0):
    try:
        return float(v) if v and str(v).strip() else default
    except Exception:
        return default

def safe_int(v, default=0):
    try:
        return int(float(v)) if v and str(v).strip() else default
    except Exception:
        return default

def run_subprocess(cmd, cwd, timeout):
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
    return send_file(os.path.join(DASHBOARD_DIR, 'landing_page.html'))

@app.route('/season')
def season_overview():
    return send_file(os.path.join(DASHBOARD_DIR, 'season_overview.html'))

@app.route('/dashboard')
def dashboard():
    return send_file(os.path.join(DASHBOARD_DIR, 'prediction_dashboard.html'))

@app.route('/predictions')
def predictions():
    return send_file(os.path.join(DASHBOARD_DIR, 'prediction_dashboard.html'))

@app.route('/driver-analysis')
def driver_analysis():
    return send_file(os.path.join(DASHBOARD_DIR, 'driver_analysis.html'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(os.path.join(DASHBOARD_DIR, filename))

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_file(os.path.join(DASHBOARD_DIR, 'css', filename))

@app.route('/drivers/<path:filename>')
def serve_driver_images(filename):
    candidates = [
        os.path.join(DASHBOARD_DIR, 'Driver', filename),
        os.path.join(DASHBOARD_DIR, 'driver', filename),
    ]
    for img_path in candidates:
        if os.path.exists(img_path):
            return send_file(img_path)
    return jsonify({'error': f'Driver image not found: {filename}'}), 404

@app.route('/f1_bg.mp4')
def serve_video():
    video_path = os.path.join(DASHBOARD_DIR, 'f1_bg.mp4')
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found in dashboards/'}), 404
    return send_file(video_path, mimetype='video/mp4', conditional=True)

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    font_path = os.path.join(DASHBOARD_DIR, 'fonts', filename)
    if not os.path.exists(font_path):
        return jsonify({'error': f'Font not found: {filename}'}), 404
    return send_file(font_path)

@app.route('/flags/<path:filename>')
def serve_flags(filename):
    flag_path = os.path.join(DASHBOARD_DIR, 'flags', filename)
    if not os.path.exists(flag_path):
        return jsonify({'error': f'Flag not found: {filename}'}), 404
    return send_file(flag_path, mimetype='image/svg+xml')

@app.route('/api/health')
def health():
    return jsonify({
        'status':        'ok',
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'base_dir':      BASE_DIR,
        'dashboard_dir': DASHBOARD_DIR,
        'venv_exists':   os.path.exists(VENV_PYTHON),
        'dash_exists':   os.path.exists(DASHBOARD_DIR),
        'flags_exist':   os.path.exists(os.path.join(DASHBOARD_DIR, 'flags')),
        'fonts_exist':   os.path.exists(os.path.join(DASHBOARD_DIR, 'fonts')),
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
            'round':           entry['round'],
            'status':          status,
            'has_predictions': os.path.exists(predictions_path(model, rn)),
            'has_metrics':     has_real_metrics(model, rn),
            'quali_end':       entry['quali_end'],
            'race_end':        entry['race_end'],
            'race_start_utc':  entry['race_start_utc'],
            'race_date_display': entry['race_date_display'],
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

    analysis_folder = os.path.join(BASE_DIR, 'outputs', 'analysis', model, race_folder_name(race))

    result = {
        'predictions':         preds,
        'feature_importance':  csv_to_list(os.path.join(folder, 'feature_importance.csv')),
        'driver_explanations': csv_to_list(os.path.join(analysis_folder, 'driver_explanations.csv')),
        'metrics': {},
    }
    mp = os.path.join(analysis_folder, 'metrics.json')
    if os.path.exists(mp):
        with open(mp, 'r', encoding='utf-8') as f:
            result['metrics'] = json.load(f)

    return jsonify(result)

# ── TRACK & WEATHER HELPERS ───────────────────────────────────────────────────

def load_track_data():
    """Returns {race_name: {circuit info + drs + lap_record}} from track_metadata.csv."""
    track_map = {}
    for row in csv_to_list(os.path.join(GOLDEN_DASH_DIR, 'track_metadata.csv')):
        race = row.get('race', '')
        if not race:
            continue
        extra = DRS_AND_RECORDS.get(race, {'drs_zones': '—', 'lap_record': '—'})
        track_map[race] = {**row, **extra}
    return track_map

def load_weather_history():
    """Returns {race_name: weather_row} from weather.csv."""
    wx_map = {}
    for row in csv_to_list(os.path.join(GOLDEN_DASH_DIR, 'weather.csv')):
        race = row.get('race', '')
        if race:
            wx_map[race] = row
    return wx_map

# ── SEASON DATA ───────────────────────────────────────────────────────────────

@app.route('/api/season/data')
def season_data():
    """
    Compute full season standings from per-race CSVs in data/golden/ (2026_*_R.csv).
    Falls back to data/golden/dashboard/driver_race_stats.csv if no per-race files exist.
    Enriches response with track metadata and weather history from dashboard CSVs.
    """
    from collections import defaultdict

    # ── 1. Load race rows ──────────────────────────────────────────────────
    race_rows_all = []

    per_race_files = sorted(glob.glob(os.path.join(GOLDEN_DIR, '2026_*_R.csv')))
    if per_race_files:
        for fpath in per_race_files:
            race_rows_all.extend(csv_to_list(fpath))
    else:
        # Fallback: combined driver_race_stats.csv
        fallback = os.path.join(GOLDEN_DASH_DIR, 'driver_race_stats.csv')
        if os.path.exists(fallback):
            race_rows_all = csv_to_list(fallback)

    if not race_rows_all:
        return jsonify({'error': 'No race result data found in data/golden/'}), 404

    # ── 2. Group by race ────────────────────────────────────────────────────
    race_results = defaultdict(list)
    for r in race_rows_all:
        race = r.get('race', '').strip()
        if race:
            race_results[race].append(r)

    # Sort each race by finishing position
    for race in race_results:
        race_results[race].sort(key=lambda x: safe_float(x.get('position', '99'), 99))

    # Determine round order
    def get_round(race_name):
        rows = race_results[race_name]
        for r in rows:
            v = safe_int(r.get('round', '0'))
            if v:
                return v
        entry = next((e for e in F1_2026_SCHEDULE if e['race'] == race_name), None)
        return entry['round'] if entry else 999

    round_order = sorted(race_results.keys(), key=get_round)

    # ── 3. Compute standings & progressions ────────────────────────────────
    all_drivers = set()
    for rows in race_results.values():
        for r in rows:
            d = r.get('driver', '').strip()
            if d:
                all_drivers.add(d)
    all_drivers.discard('')

    driver_cumul = defaultdict(float)
    driver_wins  = defaultdict(int)
    driver_pods  = defaultdict(int)
    driver_team  = {}
    driver_prog  = defaultdict(list)
    con_cumul    = defaultdict(float)
    con_wins     = defaultdict(int)
    con_prog     = defaultdict(list)
    race_summaries = []

    for race_name in round_order:
        rows = race_results[race_name]
        race_pts_map = {}
        for r in rows:
            d = r.get('driver', '').strip()
            if not d:
                continue
            pts = safe_float(r.get('points', '0'))
            race_pts_map[d] = race_pts_map.get(d, 0) + pts
            driver_team[d] = r.get('team', '')
            if r.get('winner', '') == '1':
                driver_wins[d] += 1
            if r.get('podium', '') == '1':
                driver_pods[d] += 1
            team = r.get('team', '')
            con_cumul[team] += pts
            if r.get('winner', '') == '1':
                con_wins[team] += 1

        for d in all_drivers:
            driver_cumul[d] += race_pts_map.get(d, 0)
            driver_prog[d].append(round(driver_cumul[d], 1))

        all_teams = set(driver_team.values())
        for t in all_teams:
            if t:
                con_prog[t].append(round(con_cumul.get(t, 0), 1))

        # Build podium (top 3 finishers)
        finishers = [r for r in rows if r.get('position', '').strip()]
        finishers.sort(key=lambda x: safe_float(x.get('position', '99'), 99))
        podium_rows = [r for r in finishers if r.get('podium', '') == '1'][:3]

        top10 = []
        for r in finishers[:10]:
            top10.append({
                'pos':    safe_int(r.get('position', '0')),
                'driver': r.get('driver', ''),
                'team':   r.get('team', ''),
                'grid':   safe_int(r.get('grid_position', '0')),
                'pts':    safe_int(r.get('points', '0')),
                'gained': safe_int(r.get('positions_gained', '0')),
                'status': r.get('status', 'finished'),
            })

        winner_row = finishers[0] if finishers else rows[0]
        race_summaries.append({
            'round':       get_round(race_name),
            'name':        race_name,
            'winner':      winner_row.get('driver', ''),
            'winner_team': winner_row.get('team', ''),
            'podium': [{'driver': p.get('driver', ''), 'team': p.get('team', ''),
                        'pos': safe_int(p.get('position', '0'))} for p in podium_rows],
            'top10': top10,
        })

    # ── 4. Build standings ──────────────────────────────────────────────────
    standings = sorted(
        [{'driver': d, 'team': driver_team.get(d, ''), 'pts': round(driver_cumul[d], 1),
          'wins': driver_wins[d], 'pods': driver_pods[d]}
         for d in all_drivers if driver_team.get(d)],
        key=lambda x: (-x['pts'], -x['wins'])
    )
    leader_pts = standings[0]['pts'] if standings else 0
    for i, s in enumerate(standings):
        s['pos'] = i + 1
        s['gap'] = round(s['pts'] - leader_pts, 1)

    con_pts_total = defaultdict(float)
    for rows in race_results.values():
        for r in rows:
            t = r.get('team', '')
            if t:
                con_pts_total[t] += safe_float(r.get('points', '0'))

    con_standings = sorted(
        [{'team': t, 'pts': round(con_pts_total[t], 1), 'wins': con_wins[t]}
         for t in con_pts_total],
        key=lambda x: (-x['pts'], -x['wins'])
    )
    for i, c in enumerate(con_standings):
        c['pos'] = i + 1

    con_leader_pts = con_standings[0]['pts'] if con_standings else 0
    for c in con_standings:
        c['gap'] = round(c['pts'] - con_leader_pts, 1)

    # ── 5. Season stats ─────────────────────────────────────────────────────
    most_wins = max(standings, key=lambda x: x['wins']) if standings else {}
    sched_entry = next((e for e in F1_2026_SCHEDULE if e['race'] == (race_summaries[-1]['name'] if race_summaries else '')), None)

    season_stats = {
        'races_done':        len(round_order),
        'total_races':       len(F1_2026_SCHEDULE),
        'leader':            standings[0]['driver'] if standings else '',
        'leader_pts':        standings[0]['pts']    if standings else 0,
        'leader_team':       standings[0]['team']   if standings else '',
        'con_leader':        con_standings[0]['team'] if con_standings else '',
        'con_leader_pts':    con_standings[0]['pts']  if con_standings else 0,
        'most_wins_driver':  most_wins.get('driver', ''),
        'most_wins_count':   most_wins.get('wins', 0),
        'last_race':         race_summaries[-1] if race_summaries else {},
    }

    # ── 6. Progressions (top 5) ─────────────────────────────────────────────
    top5_d = [s['driver'] for s in standings[:5]]
    top5_c = [c['team']   for c in con_standings[:5]]
    labels = [r['name'].replace(' Grand Prix', '') for r in race_summaries]

    # ── 7. Track data & weather history ─────────────────────────────────────
    track_data      = load_track_data()
    weather_history = load_weather_history()

    return jsonify({
        'driver_standings':       standings,
        'constructor_standings':  con_standings,
        'race_summaries':         race_summaries,
        'driver_progression':     {'labels': labels, 'series': {d: driver_prog[d] for d in top5_d}},
        'constructor_progression':{'labels': labels, 'series': {t: con_prog[t]    for t in top5_c}},
        'season_stats':           season_stats,
        'track_data':             track_data,
        'weather_history':        weather_history,
    })

# ── NEXT RACE ─────────────────────────────────────────────────────────────────

@app.route('/api/next-race')
def next_race():
    """
    Return info for the upcoming race: schedule entry, track metadata,
    DRS zones, lap record, and predicted weather from outputs/prediction/weather/.
    """
    now = datetime.now(timezone.utc)

    next_entry = None
    for entry in F1_2026_SCHEDULE:
        race_end_utc = parse_berlin_to_utc(entry['race_end'])
        if now < race_end_utc:
            next_entry = entry
            break

    if not next_entry:
        # Season over — return last race entry
        next_entry = F1_2026_SCHEDULE[-1]

    race_name = next_entry['race']
    race_slug = race_folder_name(race_name)

    # Predicted weather JSON
    weather_prediction = {}
    weather_candidates = [
        os.path.join(BASE_DIR, 'outputs', 'predictions', 'weather', f'{race_slug}_weather.json'),
        os.path.join(BASE_DIR, 'outputs', 'prediction', 'weather', f'{race_slug}_weather.json'),
    ]
    for wp in weather_candidates:
        if os.path.exists(wp):
            try:
                with open(wp, 'r', encoding='utf-8') as f:
                    weather_prediction = json.load(f)
            except Exception:
                pass
            break

    # Track metadata
    track_data = load_track_data()
    track_info = track_data.get(race_name, {})

    return jsonify({
        'race':               race_name,
        'round':              next_entry['round'],
        'race_start_utc':     next_entry['race_start_utc'],
        'race_date_display':  next_entry['race_date_display'],
        'quali_end':          next_entry['quali_end'],
        'race_end':           next_entry['race_end'],
        'track':              track_info,
        'weather_prediction': weather_prediction,
    })

# ── DRIVER ANALYSIS ───────────────────────────────────────────────────────────

@app.route('/api/driver-analysis/data')
def driver_analysis_data():
    ds_path = os.path.join(GOLDEN_DASH_DIR, 'driver_standings.csv')
    dr_path = os.path.join(GOLDEN_DASH_DIR, 'driver_race_stats.csv')

    if not os.path.exists(ds_path) or not os.path.exists(dr_path):
        return jsonify({
            'error': 'Driver analysis CSVs not found',
            'expected': {'driver_standings.csv': ds_path, 'driver_race_stats.csv': dr_path}
        }), 404

    return jsonify({
        'driver_standings': csv_to_list(ds_path),
        'driver_race_stats': csv_to_list(dr_path),
    })

# ── UPDATE ────────────────────────────────────────────────────────────────────

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
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"done","elapsed":elapsed})}\n\n'
                else:
                    msg = f'Pipeline ran ({elapsed}s) but predictions.csv not found. stdout: {stdout[-300:]}'
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"error","msg":msg,"elapsed":elapsed})}\n\n'
                    continue
            else:
                yield f'data: {json.dumps({"type":"progress","race":rn,"step":"prediction","status":"already_done"})}\n\n'

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
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"done","elapsed":elapsed})}\n\n'
                else:
                    msg = f'Metrics ran ({elapsed}s) but has_ground_truth=false or metrics.json missing'
                    yield f'data: {json.dumps({"type":"progress","race":rn,"step":"metrics","status":"error","msg":msg,"elapsed":elapsed})}\n\n'

        print(f"\n[UPDATE] Building dashboard data...", flush=True)
        yield f'data: {json.dumps({"type":"progress","race":"Dashboard Data","step":"build","status":"running"})}\n\n'

        ok, stdout, stderr, elapsed = run_subprocess(
            [VENV_PYTHON, '-m', 'pipelines.build_dashboard_data'],
            BASE_DIR, 300
        )

        if ok:
            yield f'data: {json.dumps({"type":"progress","race":"Dashboard Data","step":"build","status":"done","elapsed":elapsed})}\n\n'
        else:
            yield f'data: {json.dumps({"type":"progress","race":"Dashboard Data","step":"build","status":"error","msg":stderr[-400:],"elapsed":elapsed})}\n\n'

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
    print(f"  BASE_DIR        : {BASE_DIR}", flush=True)
    print(f"  DASHBOARD_DIR   : {DASHBOARD_DIR}", flush=True)
    print(f"  VENV_PYTHON     : {VENV_PYTHON}", flush=True)
    print(f"  Venv exists     : {os.path.exists(VENV_PYTHON)}", flush=True)
    print(f"  Dashboards      : {os.path.exists(DASHBOARD_DIR)}", flush=True)
    print(f"  Golden dash dir : {os.path.exists(GOLDEN_DASH_DIR)}", flush=True)
    print(f"{'='*60}\n", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)