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
        elif parsed_path.path == "/api/agents":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            agents_data = []
            if self.db_instance:
                agents_data = self.db_instance.data.get("agents", {})
            self.wfile.write(json.dumps(list(agents_data.values())).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        parsed_path = urlparse(self.path)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        response = {"success": True}

        if parsed_path.path == "/api/agents":
            if self.db_instance and "agent_id" in body:
                from .models import AgentEntity
                new_agent = AgentEntity(
                    agent_id=body["agent_id"],
                    name=body.get("name", "Unnamed Agent"),
                    role=body.get("role", "Unknown"),
                    email=body.get("email", ""),
                    budget=float(body.get("budget", 0.0)),
                    status=body.get("status", "Idle")
                )
                self.db_instance.save_agent(new_agent)
                response["agent"] = {
                    "agent_id": new_agent.agent_id,
                    "name": new_agent.name,
                    "role": new_agent.role,
                    "email": new_agent.email,
                    "budget": new_agent.budget,
                    "status": new_agent.status
                }
            else:
                self.send_response(400)
                response = {"success": False, "error": "Missing agent_id"}
        elif parsed_path.path == "/api/agents/execute":
            role = body.get("role")
            project_id = body.get("project_id")
            input_data = body.get("input_data", "")
            if role and project_id and self.db_instance:
                from .org_os import PaperclipOS
                from .google_workspace import GoogleWorkspaceClient
                workspace = GoogleWorkspaceClient("", is_mock=True)
                paperclip = PaperclipOS(self.db_instance, workspace)
                res = paperclip.trigger_agent_execution(role, project_id, input_data)
                response["result"] = res
            else:
                self.send_response(400)
                response = {"success": False, "error": "Missing role or project_id"}
        elif parsed_path.path == "/api/process/state":
            project_id = body.get("project_id")
            if project_id and self.db_instance:
                project = self.db_instance.get_project(project_id)
                if project:
                    if "step" in body:
                        project.step = int(body["step"])
                    if "approval_status" in body:
                        project.approval_status = body["approval_status"]
                    if "status" in body:
                        project.status = body["status"]
                    self.db_instance.save_project(project)
                    response["project"] = {
                        "project_id": project.project_id,
                        "status": project.status,
                        "step": project.step,
                        "approval_status": project.approval_status
                    }
                else:
                    self.send_response(404)
                    response = {"success": False, "error": "Project not found"}
            else:
                self.send_response(400)
                response = {"success": False, "error": "Missing project_id"}
        else:
            self.send_response(404)
            response = {"success": False, "error": "Not Found"}

        self.wfile.write(json.dumps(response).encode("utf-8"))

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
        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            background: linear-gradient(to right, #ffffff, #9ca3af);
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
            margin-bottom: 2.5rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
        }
        .project-card, .agent-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .project-card:hover, .agent-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(168, 85, 247, 0.4);
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.15);
        }
        .project-title, .agent-title {
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

        .badge-active { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
        .badge-idle { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }

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
        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            margin-top: 1rem;
            position: relative;
        }
        .progress-bar {
            height: 100%;
            border-radius: 3px;
            background: linear-gradient(to right, #6366f1, #a855f7);
            transition: width 0.5s ease;
        }
        .progress-text {
            font-size: 0.75rem;
            color: #a855f7;
            font-weight: 600;
            margin-top: 0.25rem;
            display: block;
            text-align: right;
        }
        .warning-label {
            font-size: 0.75rem;
            color: #f87171;
            font-weight: 600;
            background: rgba(239, 68, 68, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin-top: 0.5rem;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>BRENXIA OS</h1>
                <p style="color: #9ca3af; margin-top: 0.25rem;">Hermes & Paperclip Company OS Dashboard</p>
            </div>
            <div class="badge badge-execution" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                OS Core Active
            </div>
        </header>
        
        <main>
            <!-- Projects Section -->
            <div class="glass-card">
                <h2 class="section-title">Active Projects & 11-Step Progress</h2>
                <div class="grid" id="project-list">
                    <p style="color: #9ca3af;">Loading projects...</p>
                </div>
            </div>

            <!-- Virtual Agents Section -->
            <div class="glass-card">
                <h2 class="section-title">Virtual Specialists (AI Agents)</h2>
                <div class="grid" id="agent-list">
                    <p style="color: #9ca3af;">Loading agents...</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        const STEPS_NAMES = {
            1: "1. Initiation & Kick-off",
            2: "2. Orientation (OT)",
            3: "3. Research",
            4: "4. Strategy Formulation",
            5: "5. Planning Review",
            6: "6. Creative Production",
            7: "7. Creative Refinement",
            8: "8. Creative Review",
            9: "9. Proposal & Approval",
            10: "10. Media Execution",
            11: "11. Post-buy & Archiving"
        };

        async function fetchProjects() {
            try {
                const response = await fetch('/api/projects');
                const data = await response.json();
                const container = document.getElementById('project-list');
                
                if (data.length === 0) {
                    container.innerHTML = '<p style="color: #9ca3af;">No projects found.</p>';
                    return;
                }
                
                container.innerHTML = data.map(p => {
                    const stepNum = p.step || 1;
                    const progressPercent = Math.min(100, Math.round((stepNum / 11) * 100));
                    const stepName = STEPS_NAMES[stepNum] || `Step ${stepNum}`;
                    const hasWarnings = (!p.pd_email || !p.cd_email || p.predicted_sales === 0 || p.predicted_sales === "");

                    return `
                        <div class="project-card">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                                <span class="badge badge-${p.importance.toLowerCase()}">${p.importance}</span>
                                <span class="badge badge-${p.status.toLowerCase()}">${p.status}</span>
                            </div>
                            <div class="project-title">${p.project_name}</div>
                            <div style="color: #a855f7; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">${p.client_name} - ${p.brand_name}</div>
                            
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: ${progressPercent}%"></div>
                            </div>
                            <span class="progress-text">${stepName} (${progressPercent}%)</span>

                            ${hasWarnings ? '<span class="warning-label">⚠️ Null Value Warning: Check Director or Budget!</span>' : ''}

                            <div class="meta-info">
                                <div class="meta-row">
                                    <span>PM:</span>
                                    <span>${p.pm_email}</span>
                                </div>
                                <div class="meta-row">
                                    <span>PD:</span>
                                    <span>${p.pd_email || 'Not Assigned'}</span>
                                </div>
                                <div class="meta-row">
                                    <span>CD:</span>
                                    <span>${p.cd_email || 'Not Assigned'}</span>
                                </div>
                                <div class="meta-row">
                                    <span>Approval:</span>
                                    <span style="font-weight: 600; color: ${p.approval_status === 'Approved' ? '#4ade80' : '#facc15'}">${p.approval_status}</span>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (err) {
                console.error(err);
                document.getElementById('project-list').innerHTML = '<p style="color: #f87171;">Failed to load project list.</p>';
            }
        }

        async function fetchAgents() {
            try {
                const response = await fetch('/api/agents');
                const data = await response.json();
                const container = document.getElementById('agent-list');
                
                if (data.length === 0) {
                    container.innerHTML = '<p style="color: #9ca3af;">No virtual specialists registered.</p>';
                    return;
                }
                
                container.innerHTML = data.map(a => `
                    <div class="agent-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <span class="badge badge-${a.status.toLowerCase()}">${a.status}</span>
                            <span style="font-size: 0.75rem; color: #9ca3af; font-weight: 600;">${a.role}</span>
                        </div>
                        <div class="agent-title">${a.name}</div>
                        <div style="color: #6366f1; font-size: 0.85rem; margin-bottom: 1rem;">${a.email}</div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem; font-size: 0.85rem; color: #d1d5db; display: flex; justify-content: space-between;">
                            <span>Monthly Cost Limit:</span>
                            <span style="font-weight: 600; color: #a855f7;">$${a.budget.toLocaleString()}</span>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
                document.getElementById('agent-list').innerHTML = '<p style="color: #f87171;">Failed to load virtual specialists.</p>';
            }
        }
        
        fetchProjects();
        fetchAgents();
        setInterval(() => {
            fetchProjects();
            fetchAgents();
        }, 5000);
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
