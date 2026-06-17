import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from .config import Config
from .models import Project

logger = logging.getLogger("vibe_cording.google_workspace")

class GoogleWorkspaceClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.is_mock = config.MOCK_MODE
        self.credentials_path = config.GOOGLE_CREDENTIALS_FILE
        self.shared_drive_id = config.SHARED_DRIVE_ROOT_ID
        self.company_master_email = config.COMPANY_MASTER_EMAIL

        if self.is_mock:
            logger.info("Initializing GoogleWorkspaceClient in MOCK simulation mode.")
            self.drive_service = None
            self.sheets_service = None
            self.directory_service = None
        else:
            logger.info(f"Initializing GoogleWorkspaceClient with credentials at: {self.credentials_path}")
            try:
                # Setup basic Google OAuth Scopes for Drive and Sheets
                scopes = [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/spreadsheets"
                ]
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=scopes
                )
                self.drive_service = build("drive", "v3", credentials=self.credentials)
                self.sheets_service = build("sheets", "v4", credentials=self.credentials)
                logger.info("Google Drive and Sheets API services successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Drive/Sheets API services: {e}. Falling back to MOCK mode.")
                self.is_mock = True

            # Setup Directory API client (optional, with domain-wide delegation)
            try:
                directory_creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=["https://www.googleapis.com/auth/admin.directory.user.readonly"],
                    subject=self.company_master_email
                )
                self.directory_service = build("admin", "directory_v1", credentials=directory_creds)
                logger.info("Google Workspace Directory API service initialized.")
            except Exception as dir_err:
                logger.warning(f"Workspace Directory API DWD credentials not available: {dir_err}. Directory services will be disabled.")
                self.directory_service = None

    def _get_or_create_folder(self, name: str, parent_id: str) -> str:
        """Finds or creates a folder under a parent folder."""
        if self.is_mock:
            return f"mock_{name.replace(' ', '_')}_folder_id"

        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
        list_args: Dict[str, Any] = {
            "q": query,
            "spaces": "drive",
            "fields": "files(id, name)"
        }
        if self.shared_drive_id and self.shared_drive_id != "root":
            list_args["supportsAllDrives"] = True
            list_args["includeItemsFromAllDrives"] = True
            list_args["corpora"] = "drive"
            list_args["driveId"] = self.shared_drive_id

        try:
            results = self.drive_service.files().list(**list_args).execute()
            files = results.get("files", [])
            if files:
                folder_id = files[0]["id"]
                logger.info(f"Found existing folder '{name}' with ID '{folder_id}'")
                return folder_id
            
            # Create folder if it does not exist
            metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id]
            }
            create_args: Dict[str, Any] = {"body": metadata, "fields": "id"}
            if self.shared_drive_id and self.shared_drive_id != "root":
                create_args["supportsAllDrives"] = True

            file_obj = self.drive_service.files().create(**create_args).execute()
            folder_id = file_obj.get("id", "")
            logger.info(f"Created folder '{name}' with ID '{folder_id}' under parent '{parent_id}'")
            return folder_id
        except HttpError as e:
            logger.error(f"Failed to find or create folder '{name}': {e}")
            raise e

    def create_project_folders(self, project: Project) -> Dict[str, str]:
        """Creates standard project folders on Google Drive using Service Account."""
        subfolders = [
            "00.\uace0\uac1d\uc0ac \uc81c\uacf5\uc790\ub8cc",
            "01.\uc81c\uc548",
            "02.\uae30\ud68d",
            "03.\uc81c\uc791",
            "04.\ubbf8\ub514\uc5b4",
            "05.\ud589\uc815",
            "06.PMS"
        ]
        
        # Folder format: 260617_Client_Brand_ProjectName
        yymmdd = project.period_start[:6] if (project.period_start and len(project.period_start) >= 6) else "260617"
        root_name = f"{yymmdd}_{project.client_name}_{project.brand_name}_{project.project_name}"
        year_name = f"20{yymmdd[:2]}"

        folder_ids: Dict[str, str] = {}

        if self.is_mock:
            folder_ids["root"] = f"mock_{project.project_id}_root_id"
            for folder in subfolders:
                folder_ids[folder] = f"mock_{folder}_id"
            logger.info(f"[MOCK] Created folder hierarchy for project '{root_name}'")
            return folder_ids

        try:
            # 1. Resolve or create top-level 'project' folder
            project_top_id = self._get_or_create_folder("project", self.shared_drive_id)
            # 2. Resolve or create year folder (e.g. 2026) under 'project'
            year_folder_id = self._get_or_create_folder(year_name, project_top_id)

            # 3. Create the project root folder
            root_metadata = {
                "name": root_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [year_folder_id]
            }
            create_args: Dict[str, Any] = {"body": root_metadata, "fields": "id"}
            if self.shared_drive_id and self.shared_drive_id != "root":
                create_args["supportsAllDrives"] = True
            
            root_folder = self.drive_service.files().create(**create_args).execute()
            root_id = root_folder.get("id", "")
            folder_ids["root"] = root_id

            # 4. Create standard subfolders and their old version archives
            for folder in subfolders:
                sub_metadata = {
                    "name": folder,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [root_id]
                }
                sub_args: Dict[str, Any] = {"body": sub_metadata, "fields": "id"}
                if self.shared_drive_id and self.shared_drive_id != "root":
                    sub_args["supportsAllDrives"] = True
                
                sub_folder = self.drive_service.files().create(**sub_args).execute()
                sub_id = sub_folder.get("id", "")
                folder_ids[folder] = sub_id

                # Create '_이전버전_아카이브' for strategic folders
                if folder in ["02.\uae30\ud68d", "03.\uc81c\uc791"]:
                    archive_metadata = {
                        "name": "_\uc774\uc804\ubcac\uc804_\uc544\uce74\uc774\ube0c",
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [sub_id]
                    }
                    archive_args = {"body": archive_metadata, "fields": "id"}
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        archive_args["supportsAllDrives"] = True
                    self.drive_service.files().create(**archive_args).execute()

            logger.info(f"Successfully created folder hierarchy for project ID '{project.project_id}'")
            return folder_ids
        except Exception as e:
            logger.error(f"Failed to create project folder hierarchy: {e}")
            raise e

    def sync_permissions(self, project: Project, root_folder_id: str) -> None:
        """Shares project root folder with PM CD PD and team members."""
        if self.is_mock:
            logger.info(f"[MOCK] Synced write permissions on folder '{root_folder_id}' for PM: {project.pm_email}")
            return

        emails = [project.pm_email, project.pd_email, project.cd_email] + project.members
        unique_emails = set(filter(None, emails))

        for email in unique_emails:
            try:
                permission = {
                    "type": "user",
                    "role": "writer",
                    "emailAddress": email
                }
                create_args: Dict[str, Any] = {
                    "fileId": root_folder_id,
                    "body": permission
                }
                if self.shared_drive_id and self.shared_drive_id != "root":
                    create_args["supportsAllDrives"] = True
                self.drive_service.permissions().create(**create_args).execute()
                logger.info(f"Granted writer permission to {email} on project folder {root_folder_id}")
            except Exception as e:
                logger.warning(f"Failed to share project folder {root_folder_id} with {email}: {e}")

    def upload_file(self, root_folder_id: str, subfolder_id: str, file_path: str, mime_type: str) -> Dict[str, str]:
        """Uploads a file to a specific folder on Google Drive using the Service Account."""
        filename = os.path.basename(file_path)
        if self.is_mock:
            logger.info(f"[MOCK] Uploaded file '{filename}' to folder '{subfolder_id}'")
            return {
                "file_id": f"mock_uploaded_{filename}_id",
                "web_view_link": f"https://drive.google.com/open?id=mock_uploaded_{filename}_id",
                "filename": filename
            }

        try:
            file_metadata = {
                "name": filename,
                "parents": [subfolder_id]
            }
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
            create_args: Dict[str, Any] = {
                "body": file_metadata,
                "media_body": media,
                "fields": "id, webViewLink"
            }
            if self.shared_drive_id and self.shared_drive_id != "root":
                create_args["supportsAllDrives"] = True

            uploaded_file = self.drive_service.files().create(**create_args).execute()
            file_id = uploaded_file.get("id", "")
            web_view_link = uploaded_file.get("webViewLink", "")
            logger.info(f"File '{filename}' successfully uploaded. ID: {file_id}")
            return {
                "file_id": file_id,
                "web_view_link": web_view_link,
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Failed to upload file '{filename}' to Google Drive: {e}")
            raise e

    def setup_pms_spreadsheet(self, project: Project, pms_folder_id: str) -> str:
        """Finds or copies the company WPMS template for the client."""
        # Standard filename: BRENXIA WPMS_[ClientName]
        pms_filename = f"BRENXIA WPMS_{project.client_name}_{project.project_name}"

        if self.is_mock:
            return f"mock_{project.client_name}_pms_spreadsheet_id"

        try:
            # 1. Search for existing PMS sheet in PMS folder
            query = f"name = '{pms_filename}' and mimeType = 'application/vnd.google-apps.spreadsheet' and '{pms_folder_id}' in parents and trashed = false"
            list_args: Dict[str, Any] = {
                "q": query,
                "spaces": "drive",
                "fields": "files(id, name)"
            }
            if self.shared_drive_id and self.shared_drive_id != "root":
                list_args["supportsAllDrives"] = True
                list_args["includeItemsFromAllDrives"] = True
                list_args["corpora"] = "drive"
                list_args["driveId"] = self.shared_drive_id

            results = self.drive_service.files().list(**list_args).execute()
            files = results.get("files", [])
            if files:
                spreadsheet_id = files[0]["id"]
                logger.info(f"Found existing PMS spreadsheet '{pms_filename}' with ID '{spreadsheet_id}'")
                return spreadsheet_id

            # 2. Copy master template
            template_id = self.config.WPMS_TEMPLATE_ID
            copy_metadata = {
                "name": pms_filename,
                "parents": [pms_folder_id]
            }
            copy_args: Dict[str, Any] = {
                "fileId": template_id,
                "body": copy_metadata,
                "fields": "id"
            }
            if self.shared_drive_id and self.shared_drive_id != "root":
                copy_args["supportsAllDrives"] = True

            copied_file = self.drive_service.files().copy(**copy_args).execute()
            spreadsheet_id = copied_file.get("id", "")
            logger.info(f"PMS spreadsheet copied from template ID '{template_id}'. New ID: {spreadsheet_id}")
            return spreadsheet_id
        except Exception as e:
            logger.error(f"Failed to setup PMS spreadsheet: {e}")
            raise e

    def sync_pms_permissions(self, project: Project, spreadsheet_id: str) -> None:
        """Grants write permission to CD/PD, and read permission to PM and team members."""
        if self.is_mock:
            logger.info(f"[MOCK] Synced PMS permissions on sheet '{spreadsheet_id}'")
            return

        # CD and PD get 'writer' permission
        writers = set(filter(None, [project.pd_email, project.cd_email]))
        # PM and other members get 'reader' permission
        readers = set(filter(None, [project.pm_email] + project.members))

        # Perform sharing
        for writer in writers:
            try:
                permission = {"type": "user", "role": "writer", "emailAddress": writer}
                self.drive_service.permissions().create(
                    fileId=spreadsheet_id, body=permission, supportsAllDrives=True
                ).execute()
                logger.info(f"Granted write permission on PMS sheet to CD/PD: {writer}")
            except Exception as e:
                logger.warning(f"Failed to share PMS sheet as writer with {writer}: {e}")

        for reader in readers:
            if reader in writers:
                continue  # Writer role overrides reader role
            try:
                permission = {"type": "user", "role": "reader", "emailAddress": reader}
                self.drive_service.permissions().create(
                    fileId=spreadsheet_id, body=permission, supportsAllDrives=True
                ).execute()
                logger.info(f"Granted read-only permission on PMS sheet to team member: {reader}")
            except Exception as e:
                logger.warning(f"Failed to share PMS sheet as reader with {reader}: {e}")
