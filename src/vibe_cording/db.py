import os
import json
import logging
from typing import Dict, Any, List, Optional
from .models import Project, WBSTask, ResourceMM

logger = logging.getLogger("vibe_cording.db")

class LocalJSONDatabase:
    def __init__(self, filepath: str = "data/db.json") -> None:
        self.filepath = filepath
        self.data: Dict[str, Any] = {
            "projects": {},
            "tasks": {},
            "resource_mms": {}
        }
        self.load()

    def load(self) -> None:
        """Loads data from the JSON file."""
        if not os.path.exists(self.filepath):
            logger.info(f"Database file {self.filepath} not found. Starting with empty database.")
            parent_dir = os.path.dirname(self.filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            self.save()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self.data = {
                    "projects": raw_data.get("projects", {}),
                    "tasks": raw_data.get("tasks", {}),
                    "resource_mms": raw_data.get("resource_mms", {})
                }
            logger.info(f"Database successfully loaded from {self.filepath}.")
        except Exception as e:
            logger.error(f"Failed to load database from {self.filepath}: {e}")

    def save(self) -> None:
        """Saves current database state to the JSON file using atomic write."""
        try:
            tmp_filepath = f"{self.filepath}.tmp"
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_filepath, self.filepath)
            logger.debug(f"Database successfully saved to {self.filepath}.")
        except Exception as e:
            logger.error(f"Failed to save database to {self.filepath}: {e}")
            if os.path.exists(f"{self.filepath}.tmp"):
                try:
                    os.remove(f"{self.filepath}.tmp")
                except OSError:
                    pass

    # Project Operations
    def get_project(self, project_id: str) -> Optional[Project]:
        project_dict = self.data["projects"].get(project_id)
        if project_dict:
            return Project.from_dict(project_dict)
        return None

    def save_project(self, project: Project) -> None:
        self.data["projects"][project.project_id] = project.to_dict()
        self.save()

    def get_all_projects(self) -> List[Project]:
        return [Project.from_dict(p) for p in self.data["projects"].values()]

    # Task Operations
    def get_task(self, task_id: str) -> Optional[WBSTask]:
        task_dict = self.data["tasks"].get(task_id)
        if task_dict:
            return WBSTask.from_dict(task_dict)
        return None

    def get_tasks_for_project(self, project_id: str) -> List[WBSTask]:
        return [
            WBSTask.from_dict(t)
            for t in self.data["tasks"].values()
            if t.get("project_id") == project_id
        ]

    def save_task(self, task: WBSTask) -> None:
        self.data["tasks"][task.task_id] = task.to_dict()
        self.save()

    def delete_task(self, task_id: str) -> None:
        if task_id in self.data["tasks"]:
            del self.data["tasks"][task_id]
            self.save()

    # ResourceMM Operations
    def get_resource_mms_for_project(self, project_id: str) -> List[ResourceMM]:
        return [
            ResourceMM.from_dict(m)
            for m in self.data["resource_mms"].values()
            if m.get("project_id") == project_id
        ]

    def save_resource_mm(self, resource_mm: ResourceMM) -> None:
        key = f"{resource_mm.project_id}_{resource_mm.email}_{resource_mm.month}"
        self.data["resource_mms"][key] = resource_mm.to_dict()
        self.save()
