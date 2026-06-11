import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Optional
from .db import LocalJSONDatabase

logger = logging.getLogger("vibe_cording.dashboard")

class DashboardHandler(BaseHTTPRequestHandler):
    db_instance: Optional[LocalJSONDatabase] = None

    def log_message(self, format, *args):
        # Suppress standard logging to stdout to keep terminal clean
        logger.debug(format % args)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self._get_html_content().encode("utf-8"))
        elif parsed_path.path == "/api/projects":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            projects_data = []
            if self.db_instance:
                projects_data = self.db_instance.data.get("projects", {})
            self.wfile.write(json.dumps(list(projects_data.values())).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def _get_html_content(self) -> str:
        # A beautiful Glassmorphism HTML page designed with Outfit and Inter fonts
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRENXIA WPMS Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #090d16 0%, #111827 100%);
            color: #f3f4f6;
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            margin-bottom: 3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 2.5rem;
            background: linear-gradient(to right, #a855f7, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        .project-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        .project-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(168, 85, 247, 0.4);
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.15);
        }
        .project-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-proposal { background: rgba(234, 179, 8, 0.2); color: #facc15; }
        .badge-execution { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
        .badge-paused { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .badge-lost { background: rgba(156, 163, 175, 0.2); color: #d1d5db; }
        .badge-closure { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
        
        .badge-standard { border: 1px solid rgba(255, 255, 255, 0.2); color: #d1d5db; }
        .badge-critical { border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171; }

        .meta-info {
            margin-top: 1rem;
            font-size: 0.85rem;
            color: #9ca3af;
        }
        .meta-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.25rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>BRENXIA</h1>
                <p style="color: #9ca3af; margin-top: 0.25rem;">Workforce & Project Management System</p>
            </div>
            <div class="badge badge-execution" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                PM Agent Active
            </div>
        </header>
        
        <main>
            <div class="glass-card">
                <h2 style="font-family: 'Outfit', sans-serif; margin-bottom: 1.5rem; font-weight: 600;">Active Projects</h2>
                <div class="grid" id="project-list">
                    <p style="color: #9ca3af;">Loading projects...</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        async function fetchProjects() {
            try {
                const response = await fetch('/api/projects');
                const data = await response.json();
                const container = document.getElementById('project-list');
                
                if (data.length === 0) {
                    container.innerHTML = '<p style="color: #9ca3af;">No projects found.</p>';
                    return;
                }
                
                container.innerHTML = data.map(p => `
                    <div class="project-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <span class="badge badge-${p.importance.toLowerCase()}">${p.importance}</span>
                            <span class="badge badge-${p.status.toLowerCase()}">${p.status}</span>
                        </div>
                        <div class="project-title">${p.project_name}</div>
                        <div style="color: #a855f7; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">${p.client_name} - ${p.brand_name}</div>
                        
                        <div class="meta-info">
                            <div class="meta-row">
                                <span>PM:</span>
                                <span>${p.pm_email}</span>
                            </div>
                            <div class="meta-row">
                                <span>PD:</span>
                                <span>${p.pd_email}</span>
                            </div>
                            <div class="meta-row">
                                <span>CD:</span>
                                <span>${p.cd_email}</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
                document.getElementById('project-list').innerHTML = '<p style="color: #f87171;">Failed to load project list.</p>';
            }
        }
        
        fetchProjects();
        setInterval(fetchProjects, 5000);
    </script>
</body>
</html>
"""

class DashboardServer:
    def __init__(self, host: str, port: int, db: LocalJSONDatabase):
        self.host = host
        self.port = port
        self.db = db
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        # Bind the database instance to the handler class
        DashboardHandler.db_instance = self.db
        self.server = HTTPServer((self.host, self.port), DashboardHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"Dashboard server started successfully at http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Dashboard server stopped successfully.")
