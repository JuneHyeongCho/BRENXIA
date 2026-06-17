import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .pm_agent import PMAgent
from .config import Config

app = FastAPI(title="BRENXIA PMO Agent API", version="1.0.0")
config = Config()

# Initialize PM Agent
# Use DB path from config or default local file
db_path = os.environ.get("DB_PATH", "data/db.json")
agent = PMAgent(db_path=db_path)

# Pydantic Schemas for Requests
class ProjectCreateRequest(BaseModel):
    client_name: str
    brand_name: str
    project_name: str
    pm_email: str
    pd_email: Optional[str] = None
    cd_email: Optional[str] = None
    members: Optional[List[str]] = Field(default_factory=list)
    predicted_sales: Optional[float] = 0.0
    predicted_purchases: Optional[float] = 0.0
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    business_sector: Optional[str] = None
    department: Optional[str] = None

class DeliverableShareRequest(BaseModel):
    project_id: str
    file_path: str
    category: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "mock_mode": agent.config.MOCK_MODE}

@app.post("/projects")
def create_project(req: ProjectCreateRequest):
    try:
        project = agent.request_project_creation(
            client_name=req.client_name,
            brand_name=req.brand_name,
            project_name=req.project_name,
            pm_email=req.pm_email,
            pd_email=req.pd_email,
            cd_email=req.cd_email,
            members=req.members,
            predicted_sales=req.predicted_sales,
            predicted_purchases=req.predicted_purchases,
            period_start=req.period_start,
            period_end=req.period_end,
            business_sector=req.business_sector,
            department=req.department
        )
        return {
            "status": "success",
            "project_id": project.project_id,
            "drive_folder_id": project.drive_folder_id,
            "spreadsheet_id": project.spreadsheet_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deliverables")
def share_deliverable(req: DeliverableShareRequest):
    try:
        # Check if the local file exists before attempting drive upload
        # In real mode, it must exist. In mock mode, we simulate.
        if not agent.config.MOCK_MODE and not os.path.exists(req.file_path):
            raise HTTPException(status_code=400, detail=f"File not found at path: {req.file_path}")
            
        result = agent.share_deliverable(
            project_id=req.project_id,
            file_path=req.file_path,
            category=req.category
        )
        return {
            "status": "success",
            "file_id": result.get("file_id"),
            "web_view_link": result.get("web_view_link"),
            "filename": result.get("filename")
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}")
def get_project(project_id: str):
    project = agent.db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID '{project_id}' not found.")
    return project.to_dict()

def start():
    import uvicorn
    uvicorn.run(
        "vibe_cording.app:app",
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        reload=False
    )
