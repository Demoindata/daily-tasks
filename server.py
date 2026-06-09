#!/usr/bin/env python3
"""Simple server that serves daily_tasks.html and persists data to a JSON file."""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data_backup.json')
HTML_FILE = os.path.join(os.path.dirname(__file__), 'daily_tasks.html')

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'{}')
            return

        if self.path == '/':
            self.path = '/daily_tasks.html'

        if self.path == '/daily_tasks.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(HTML_FILE, 'rb') as f:
                self.wfile.write(f.read())
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/data':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    port = 18920
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'Server running at http://127.0.0.1:{port}/daily_tasks.html')
    print(f'Data backup: {DATA_FILE}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
        server.server_close()
