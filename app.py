import os
import threading
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_file, Response
from dotenv import load_dotenv
import scanner

load_dotenv()

app = Flask(__name__)

scan_status = {}
scan_result = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.abspath(os.path.join(BASE_DIR, 'reports'))

def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False

@app.route('/')
def index():
    html_path = os.path.join(BASE_DIR, 'index.html')
    if not os.path.exists(html_path):
        return 'Interface introuvable', 404
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return Response(content, mimetype='text/html')

@app.route('/api/check-zap')
def check_zap():
    ok = scanner.check_zap_running()
    return jsonify({'running': ok})

@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.get_json(silent=True) or {}
    url  = data.get('url', '').strip()
    do_spider = bool(data.get('spider', True))
    do_active = bool(data.get('active', True))

    if not url:
        return jsonify({'error': 'URL manquante'}), 400

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    if not is_valid_url(url):
        return jsonify({'error': 'Format d\'URL invalide'}), 400

    scan_status[url] = {'step': 'connect', 'pct': 0, 'msg': 'Demarrage...', 'done': False, 'error': None}
    scan_result[url] = None

    def progress(step, pct, msg):
        scan_status[url] = {'step': step, 'pct': pct, 'msg': msg, 'done': False, 'error': None}

    def run():
        try:
            result = scanner.run_scan(url, do_spider, do_active, progress)
            scan_result[url] = result
            scan_status[url]['done'] = True
        except Exception as e:
            scan_status[url]['error'] = str(e)
            scan_status[url]['done']  = True

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'started': True, 'url': url})

@app.route('/api/status')
def get_status():
    url = request.args.get('url', '')
    return jsonify(scan_status.get(url, {'error': 'URL inconnue'}))

@app.route('/api/result')
def get_result():
    url = request.args.get('url', '')
    r   = scan_result.get(url)
    if not r:
        return jsonify({'error': 'Pas de resultat'})
    return jsonify({
        'target':      r['target'],
        'total':       r['total'],
        'counts':      r['counts'],
        'alerts':      r['alerts'][:50],
        'report_path': r['report_path']
    })

@app.route('/api/report')
def download_report():
    url = request.args.get('url', '')
    r   = scan_result.get(url)
    if not r or not r.get('report_path'):
        return 'Rapport introuvable', 404
    
    report_path = os.path.abspath(r['report_path'])
    # Vérification anti-path-traversal : le fichier doit se trouver dans REPORTS_DIR
    if not report_path.startswith(REPORTS_DIR) or not os.path.exists(report_path):
        return 'Fichier de rapport non autorise ou introuvable', 403

    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')

    print(f"Interface ZAP Scanner disponible sur http://{host}:{port}")
    app.run(debug=debug, port=port, host=host)