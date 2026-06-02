#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Task Reminder — local API server + launcher

用法:
  python daily_tasks.py              启动工作区服务并打开任务清单
  python daily_tasks.py --browse     仅打开浏览器（假设服务已在运行）
  python daily_tasks.py --setup      开启工作日 09:00 自动提醒
  python daily_tasks.py --remove     关闭自动提醒
  python daily_tasks.py --status     查看定时任务状态
"""

import json, os, sys, webbrowser, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

DATA_DIR = os.path.join(os.path.expanduser("~"), ".daily_tasks")
TASKS_FILE      = os.path.join(DATA_DIR, "tasks.json")
COMPLETIONS_FILE = os.path.join(DATA_DIR, "completions.json")
TEMP_TASKS_FILE  = os.path.join(DATA_DIR, "temp_tasks.json")
CATEGORIES_FILE  = os.path.join(DATA_DIR, "categories.json")
SETTINGS_FILE    = os.path.join(DATA_DIR, "settings.json")
SCHEDULE_NAME = "DailyTaskReminder"
PORT = 18920

DEFAULT_CATEGORIES = ['工作','运维','学习','个人','其他']
DEFAULT_SETTINGS   = {'theme':'light','workdays':[1,2,3,4,5]}

_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_tasks.html")

# ── File I/O ──

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    ensure_dir()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── HTTP Server ──

FILES = {
    'tasks':       (TASKS_FILE, []),
    'completions':  (COMPLETIONS_FILE, {}),
    'tempTasks':    (TEMP_TASKS_FILE, {}),
    'categories':   (CATEGORIES_FILE, list(DEFAULT_CATEGORIES)),
    'settings':     (SETTINGS_FILE, dict(DEFAULT_SETTINGS)),
}

class Handler(BaseHTTPRequestHandler):
    """Serves the HTML app and JSON API for workspace persistence."""

    def do_GET(self):
        if self.path == '/api/data':
            return self._json(200, {
                k: load_json(p, d) for k, (p, d) in FILES.items()
            })
        self._serve_html()

    def do_POST(self):
        if self.path == '/api/data':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            for k in FILES:
                if k in body:
                    save_json(FILES[k][0], body[k])
            return self._json(200, {'ok': True})
        self.send_error(404)

    def do_OPTIONS(self):
        self._cors()
        self.send_response(204)
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, status, data):
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        with open(_HTML_PATH, 'rb') as f:
            self.wfile.write(f.read())

    def log_message(self, *a):
        pass  # quiet

# ── Scheduled task ──

def schedule_exists():
    r = subprocess.run(
        f'schtasks /query /tn "{SCHEDULE_NAME}"',
        capture_output=True, text=True, timeout=15, shell=True)
    return r.returncode == 0

def schedule_install():
    script = os.path.abspath(sys.argv[0])
    python = sys.executable
    r = subprocess.run(
        f'schtasks /create /tn "{SCHEDULE_NAME}" /tr '
        f'"\\"{python}\\" \\"{script}\\" --browse" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00 /f',
        capture_output=True, text=True, timeout=15, shell=True)
    return r.returncode == 0, r.stderr if r.returncode else ""

def schedule_remove():
    subprocess.run(
        f'schtasks /delete /tn "{SCHEDULE_NAME}" /f',
        capture_output=True, timeout=15, shell=True)

# ── CLI ──

def show_help():
    print("Daily Task Reminder\n")
    print("  python daily_tasks.py              启动工作区服务并打开任务清单")
    print("  python daily_tasks.py --browse     仅打开浏览器（服务需已在运行）")
    print("  python daily_tasks.py --setup      开启工作日 09:00 自动提醒")
    print("  python daily_tasks.py --remove     关闭自动提醒")
    print("  python daily_tasks.py --status     查看定时任务状态")
    print("  python daily_tasks.py --help       显示此帮助")

if __name__ == '__main__':
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help(); sys.exit(0)
    if "--setup" in sys.argv:
        ok, e = schedule_install()
        print("OK" if ok else f"FAIL {e}"); sys.exit(0 if ok else 1)
    if "--remove" in sys.argv:
        schedule_remove(); print("OK"); sys.exit(0)
    if "--status" in sys.argv:
        print("configured" if schedule_exists() else "not configured"); sys.exit(0)
    if "--browse" in sys.argv:
        url = f'http://127.0.0.1:{PORT}'
        print(f"Opening {url} ...")
        webbrowser.open(url)
        sys.exit(0)

    # Default: start server + open browser
    ensure_dir()
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://127.0.0.1:{PORT}'
    print(f" Daily Task Reminder")
    print(f" 服务已启动 → {url}")
    print(f" 按 Ctrl+C 停止服务")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("\n服务已停止")
