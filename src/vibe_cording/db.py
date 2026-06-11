import json
import os
from typing import List, Dict, Any, Optional
from .models import Project, WBSTask, ResourceMM

class LocalJSONDatabase:
    def __init__(self, filepath: str = "data/db.json"):
        self.filepath = filepath
        self.data = {"projects": {}, "tasks": {}, "resources": {}}
        self._ensure_file_exists()
        self.load_data()

    def _ensure_file_exists(self):
        dir_name = os.path.dirname(self.filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.filepath):
            self.save_data()

    def load_data(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {"projects": {}, "tasks": {}, "resources": {}}

    def save_data(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def save_project(self, project: Project):
        self.data["projects"][project.project_id] = {
            "project_id": project.project_id,
            "client_name": project.client_name,
            "brand_name": project.brand_name,
            "project_name": project.project_name,
            "pm_email": project.pm_email,
            "importance": project.importance,
            "status": project.status,
            "pd_email": project.pd_email,
            "cd_email": project.cd_email,
            "members": project.members,
            "drive_folder_id": project.drive_folder_id,
            "spreadsheet_id": project.spreadsheet_id
        }
        self.save_data()

    def get_project(self, project_id: str) -> Optional[Project]:
        proj_dict = self.data["projects"].get(project_id)
        if not proj_dict:
            return None
        return Project(
            project_id=proj_dict["project_id"],
            client_name=proj_dict["client_name"],
            brand_name=proj_dict["brand_name"],
            project_name=proj_dict["project_name"],
            pm_email=proj_dict["pm_email"],
            importance=proj_dict["importance"],
            status=proj_dict["status"],
            pd_email=proj_dict["pd_email"],
            cd_email=proj_dict["cd_email"],
            members=proj_dict.get("members", []),
            drive_folder_id=proj_dict.get("drive_folder_id"),
            spreadsheet_id=proj_dict.get("spreadsheet_id")
        )

    def list_projects(self) -> List[Project]:
        return [self.get_project(pid) for pid in self.data["projects"]]

    def save_wbs_tasks(self, tasks: List[WBSTask]):
        for t in tasks:
            if t.project_id not in self.data["tasks"]:
                self.data["tasks"][t.project_id] = {}
            self.data["tasks"][t.project_id][t.task_id] = {
                "task_id": t.task_id,
                "project_id": t.project_id,
                "name": t.name,
                "status": t.status,
                "start_date": t.start_date,
                "end_date": t.end_date,
                "assignee": t.assignee
            }
        self.save_data()

    def list_wbs_tasks(self, project_id: str) -> List[WBSTask]:
        proj_tasks = self.data["tasks"].get(project_id, {})
        return [
            WBSTask(
                task_id=td["task_id"],
                project_id=td["project_id"],
                name=td["name"],
                status=td["status"],
                start_date=td["start_date"],
                end_date=td["end_date"],
                assignee=td["assignee"]
            )
            for td in proj_tasks.values()
        ]

    def save_resources(self, resources: List[ResourceMM]):
        for r in resources:
            if r.project_id not in self.data["resources"]:
                self.data["resources"][r.project_id] = {}
            self.data["resources"][r.project_id][r.employee_name] = {
                "project_id": r.project_id,
                "employee_name": r.employee_name,
                "role": r.role,
                "mm_value": r.mm_value,
                "days_input": r.days_input,
                "cost": r.cost
            }
        self.save_data()

    def list_resources(self, project_id: str) -> List[ResourceMM]:
        proj_res = self.data["resources"].get(project_id, {})
        return [
            ResourceMM(
                project_id=rd["project_id"],
                employee_name=rd["employee_name"],
                role=rd["role"],
                mm_value=rd["mm_value"],
                days_input=rd["days_input"],
                cost=rd["cost"]
            )
            for rd in proj_res.values()
        ]
