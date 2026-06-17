import os
import uuid
import logging
import mimetypes
from typing import List, Dict, Any, Optional
from .config import Config
from .models import Project, WBSTask
from .db import LocalJSONDatabase
from .google_workspace import GoogleWorkspaceClient

logger = logging.getLogger("vibe_cording.pm_agent")

class PMAgent:
    def __init__(self, db_path: str = "data/db.json", is_mock: Optional[bool] = None) -> None:
        self.config = Config()
        if is_mock is not None:
            self.config.MOCK_MODE = is_mock

        self.db = LocalJSONDatabase(filepath=db_path)
        self.workspace = GoogleWorkspaceClient(self.config)

    def request_project_creation(
        self,
        client_name: str,
        brand_name: str,
        project_name: str,
        pm_email: str,
        pd_email: Optional[str] = None,
        cd_email: Optional[str] = None,
        members: Optional[List[str]] = None,
        predicted_sales: float = 0.0,
        predicted_purchases: float = 0.0,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        business_sector: Optional[str] = None,
        department: Optional[str] = None
    ) -> Project:
        """Handles project creation, directory hierarchy provisioning, and PMS spreadsheet setup."""
        # Generate a unique project ID
        project_id = f"brx-{str(uuid.uuid4())[:8]}"
        
        project = Project(
            project_id=project_id,
            client_name=client_name,
            brand_name=brand_name,
            project_name=project_name,
            pm_email=pm_email,
            pd_email=pd_email,
            cd_email=cd_email,
            members=members or [],
            status="Proposal",
            predicted_sales=predicted_sales,
            predicted_purchases=predicted_purchases,
            period_start=period_start,
            period_end=period_end,
            business_sector=business_sector,
            department=department
        )

        logger.info(f"Initiating project creation: {project_id} ({client_name} - {project_name})")
        self.db.save_project(project)

        try:
            # Provision Google Drive directories
            folder_ids = self.workspace.create_project_folders(project)
            project.drive_folder_id = folder_ids.get("root")
            project.folder_ids = folder_ids

            if project.drive_folder_id:
                # Share root directory with team members
                self.workspace.sync_permissions(project, project.drive_folder_id)

                # Set up PMS spreadsheet under '06.PMS' folder
                pms_folder_id = folder_ids.get("06.PMS")
                if pms_folder_id:
                    spreadsheet_id = self.workspace.setup_pms_spreadsheet(project, pms_folder_id)
                    project.spreadsheet_id = spreadsheet_id
                    
                    if spreadsheet_id:
                        # Set CD/PD write permissions and PM/member read permissions
                        self.workspace.sync_pms_permissions(project, spreadsheet_id)

            # Save updated project details to local DB
            self.db.save_project(project)
            logger.info(f"Project creation completed successfully for ID: {project_id}")
        except Exception as e:
            logger.error(f"Failed to fully provision Google Workspace resources for project {project_id}: {e}")
            # Rollback: remove incomplete project from local DB to prevent inconsistent state
            if project.project_id in self.db.data["projects"]:
                del self.db.data["projects"][project.project_id]
                self.db.save()
            raise RuntimeError(f"Workspace provisioning failed. Project creation rolled back: {e}")

        return project

    def share_deliverable(self, project_id: str, file_path: str, category: str) -> Dict[str, str]:
        """Uploads a file to a specific folder on Google Drive and returns its webViewLink."""
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project with ID '{project_id}' not found.")

        # Re-fetch folder IDs by querying Google Drive subfolders
        # For simplicity and robust decoupling, map categories to folder names
        category_mapping = {
            "\uace0\uac1d\uc0ac\uc790\ub8cc": "00.\uace0\uac1d\uc0ac \uc81c\uacf5\uc790\ub8cc",
            "\uc81c\uc548": "01.\uc81c\uc548",
            "\uae30\ud68d": "02.\uae30\ud68d",
            "\uc81c\uc791": "03.\uc81c\uc791",
            "\ubbf8\ub514\uc5b4": "04.\ubbf8\ub514\uc5b4",
            "\ud589\uc815": "05.\ud589\uc815",
            "pms": "06.PMS"
        }

        folder_name = category_mapping.get(category, "03.\uc81c\uc791") # default to 03.제작 for deliverables

        # Mock Mode file uploading simulation
        if self.config.MOCK_MODE:
            logger.info(f"[MOCK] Simulating upload of file '{file_path}' to project category '{category}'")
            filename = os.path.basename(file_path)
            return {
                "file_id": f"mock_uploaded_{filename}_id",
                "web_view_link": f"https://drive.google.com/open?id=mock_uploaded_{filename}_id",
                "filename": filename
            }

        if not project.drive_folder_id:
            raise ValueError(f"Project '{project_id}' has no associated Google Drive root folder.")

        # Get parent folder ID on Drive using stored folder_ids instead of searching by name
        target_folder_id = project.folder_ids.get(folder_name)
        
        if not target_folder_id:
            # Fallback to project root folder if target subfolder ID is not found in DB
            target_folder_id = project.drive_folder_id
            logger.warning(f"Target subfolder ID for '{folder_name}' not found. Falling back to project root folder.")

        # Determine mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Perform upload
        upload_resp = self.workspace.upload_file(
            root_folder_id=project.drive_folder_id,
            subfolder_id=target_folder_id,
            file_path=file_path,
            mime_type=mime_type
        )
        return upload_resp
