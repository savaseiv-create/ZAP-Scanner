import os
import re
import time
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

ZAP_HOST = os.getenv('ZAP_HOST', '127.0.0.1')
ZAP_PORT = int(os.getenv('ZAP_PORT', '8080'))
API_KEY  = os.getenv('ZAP_API_KEY', '')
ZAP_URL  = f'http://{ZAP_HOST}:{ZAP_PORT}'
REPORTS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
os.makedirs(REPORTS, exist_ok=True)

NO_PROXY = {'http': None, 'https': None}

def zap_get(path, params=None):
    if params is None:
        params = {}
    if API_KEY:
        params['apikey'] = API_KEY
    r = requests.get(f'{ZAP_URL}/JSON/{path}', params=params, proxies=NO_PROXY, timeout=30)
    return r.json()

def check_zap_running():
    try:
        params = {'apikey': API_KEY} if API_KEY else {}
        r = requests.get(
            f'{ZAP_URL}/JSON/core/view/version/',
            params=params,
            proxies=NO_PROXY,
            timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False

def _sanitize_filename(target_url):
    cleaned = re.sub(r'^https?://', '', target_url)
    cleaned = re.sub(r'[^a-zA-Z0-9_\.-]', '_', cleaned)
    return cleaned[:100]

def run_scan(target_url, do_spider=True, do_active=True, progress_callback=None):
    def notify(step, pct, msg):
        if progress_callback:
            progress_callback(step, pct, msg)

    params_base = {'apikey': API_KEY} if API_KEY else {}

    # Etape 1 - Connexion
    notify('connect', 10, 'Connexion a la cible...')
    try:
        params = {**params_base, 'url': target_url}
        requests.get(
            f'{ZAP_URL}/JSON/core/action/accessUrl/',
            params=params,
            proxies=NO_PROXY,
            timeout=15
        )
    except Exception:
        pass
    time.sleep(2)
    notify('connect', 100, 'Connecte')

    # Etape 2 - Spider
    if do_spider:
        notify('spider', 0, 'Spider demarre...')
        params = {**params_base, 'url': target_url}
        r = requests.get(
            f'{ZAP_URL}/JSON/spider/action/scan/',
            params=params,
            proxies=NO_PROXY,
            timeout=30
        )
        scan_id = r.json().get('scan', '0')
        time.sleep(2)
        while True:
            try:
                status_params = {**params_base, 'scanId': scan_id}
                r = requests.get(
                    f'{ZAP_URL}/JSON/spider/view/status/',
                    params=status_params,
                    proxies=NO_PROXY,
                    timeout=10
                )
                pct = int(r.json().get('status', 100))
            except Exception:
                pct = 100
            notify('spider', pct, f'Spider {pct}%')
            if pct >= 100:
                break
            time.sleep(3)
        notify('spider', 100, 'Spider termine')
        time.sleep(2)

    # Etape 3 - Scan actif
    if do_active:
        notify('active', 0, 'Scan actif demarre...')
        params = {**params_base, 'url': target_url}
        r = requests.get(
            f'{ZAP_URL}/JSON/ascan/action/scan/',
            params=params,
            proxies=NO_PROXY,
            timeout=30
        )
        scan_id = r.json().get('scan', '0')
        time.sleep(2)
        while True:
            try:
                status_params = {**params_base, 'scanId': scan_id}
                r = requests.get(
                    f'{ZAP_URL}/JSON/ascan/view/status/',
                    params=status_params,
                    proxies=NO_PROXY,
                    timeout=10
                )
                pct = int(r.json().get('status', 100))
            except Exception:
                pct = 100
            notify('active', pct, f'Scan actif {pct}%')
            if pct >= 100:
                break
            time.sleep(5)
        notify('active', 100, 'Scan actif termine')
        time.sleep(2)

    # Etape 4 - Recuperer les alertes
    notify('alerts', 50, 'Recuperation des alertes...')
    try:
        params = {**params_base, 'baseurl': target_url}
        r = requests.get(
            f'{ZAP_URL}/JSON/core/view/alerts/',
            params=params,
            proxies=NO_PROXY,
            timeout=30
        )
        alerts = r.json().get('alerts', [])
    except Exception:
        alerts = []
    notify('alerts', 100, f'{len(alerts)} alertes trouvees')

    # Etape 5 - Rapport HTML
    notify('report', 50, 'Generation du rapport...')
    safe_name = _sanitize_filename(target_url)
    report_filename = f'{safe_name}.html'
    report_path = os.path.abspath(os.path.join(REPORTS, report_filename))
    try:
        r = requests.get(
            f'{ZAP_URL}/OTHER/core/other/htmlreport/',
            params=params_base,
            proxies=NO_PROXY,
            timeout=30
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(r.text)
    except Exception as e:
        print(f'Erreur rapport: {e}')
    notify('report', 100, 'Rapport sauvegarde')

    # Compter par severite
    counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
    for a in alerts:
        risk = a.get('risk', 'Informational')
        if risk in counts:
            counts[risk] += 1

    # Nouvelle session
    try:
        requests.get(
            f'{ZAP_URL}/JSON/core/action/newSession/',
            params=params_base,
            proxies=NO_PROXY,
            timeout=10
        )
    except Exception:
        pass

    return {
        'target':      target_url,
        'alerts':      alerts[:50],
        'counts':      counts,
        'report_path': report_path,
        'total':       len(alerts)
    }