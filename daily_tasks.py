#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Daily Task Reminder Launcher  — opens the HTML UI in browser,
handles data migration from tasks.json, and manages Windows
scheduled task for weekday 09:00 auto-start.
"""

import json, os, sys, subprocess, base64, webbrowser

DATA_DIR      = os.path.join(os.path.expanduser("~"), ".daily_tasks")
TASKS_FILE    = os.path.join(DATA_DIR, "tasks.json")
COMPLETIONS_FILE = os.path.join(DATA_DIR, "completions.json")
SCHEDULE_NAME = "DailyTaskReminder"

# ── Data ──

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None

# ─── Scheduled task (Windows) ────────────────────────────────────

def schedule_exists():
    r = subprocess.run(
        f'schtasks /query /tn "{SCHEDULE_NAME}"',
        capture_output=True, text=True, timeout=15, shell=True)
    return r.returncode == 0

def schedule_install():
    # Resolve path to THIS script so the scheduled task runs the launcher
    script = os.path.abspath(sys.argv[0])
    python = sys.executable
    r = subprocess.run(
        f'schtasks /create /tn "{SCHEDULE_NAME}" /tr '
        f'"\\"{python}\\" \\"{script}\\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00 /f',
        capture_output=True, text=True, timeout=15, shell=True)
    return r.returncode == 0, r.stderr if r.returncode else ""

def schedule_remove():
    subprocess.run(
        f'schtasks /delete /tn "{SCHEDULE_NAME}" /f',
        capture_output=True, timeout=15, shell=True)

# ── Launch HTML ──

def launch():
    """Open daily_tasks.html in browser, passing existing task data for migration."""
    ensure_data_dir()

    # Read existing data
    tasks_data = load_json(TASKS_FILE)
    completions_data = load_json(COMPLETIONS_FILE)

    # Build query params (base64 to avoid encoding issues)
    params = {}
    if tasks_data:
        params["data"] = base64.urlsafe_b64encode(
            json.dumps(tasks_data, ensure_ascii=False).encode()).decode()
    if completions_data and isinstance(completions_data, dict) and len(completions_data) > 0:
        params["completions"] = base64.urlsafe_b64encode(
            json.dumps(completions_data, ensure_ascii=False).encode()).decode()

    # Build file URL with params
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_tasks.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    if params:
        file_url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

    webbrowser.open(file_url)

# ── CLI ──

def help():
    print("Daily Task Reminder\n")
    print("  python daily_tasks.py              启动任务清单")
    print("  python daily_tasks.py --setup       开启工作日 09:00 自动提醒")
    print("  python daily_tasks.py --remove      关闭自动提醒")
    print("  python daily_tasks.py --status      查看定时任务状态")

if __name__ == "__main__":
    ensure_data_dir()

    if "--help" in sys.argv or "-h" in sys.argv:
        help(); sys.exit(0)
    if "--setup" in sys.argv:
        ok, e = schedule_install()
        print("OK" if ok else f"FAIL {e}")
        sys.exit(0 if ok else 1)
    if "--remove" in sys.argv:
        schedule_remove(); print("OK"); sys.exit(0)
    if "--status" in sys.argv:
        print("configured" if schedule_exists() else "not configured")
        sys.exit(0)

    launch()
