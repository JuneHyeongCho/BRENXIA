from typing import List, Dict, Any, Optional

class Project:
    def __init__(
        self,
        project_id: str,
        client_name: str,
        brand_name: str,
        project_name: str,
        pm_email: str,
        pd_email: Optional[str] = None,
        cd_email: Optional[str] = None,
        members: Optional[List[str]] = None,
        status: str = "Proposal",
        drive_folder_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None,
        folder_ids: Optional[Dict[str, str]] = None,
        predicted_sales: float = 0.0,
        predicted_purchases: float = 0.0,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        business_sector: Optional[str] = None,
        department: Optional[str] = None
    ) -> None:
        self.project_id = project_id
        self.client_name = client_name
        self.brand_name = brand_name
        self.project_name = project_name
        self.pm_email = pm_email
        self.pd_email = pd_email
        self.cd_email = cd_email
        self.members = members or []
        self.status = status
        self.drive_folder_id = drive_folder_id
        self.spreadsheet_id = spreadsheet_id
        self.folder_ids = folder_ids or {}
        self.predicted_sales = predicted_sales
        self.predicted_purchases = predicted_purchases
        self.period_start = period_start
        self.period_end = period_end
        self.business_sector = business_sector
        self.department = department

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "client_name": self.client_name,
            "brand_name": self.brand_name,
            "project_name": self.project_name,
            "pm_email": self.pm_email,
            "pd_email": self.pd_email,
            "cd_email": self.cd_email,
            "members": self.members,
            "status": self.status,
            "drive_folder_id": self.drive_folder_id,
            "spreadsheet_id": self.spreadsheet_id,
            "folder_ids": self.folder_ids,
            "predicted_sales": self.predicted_sales,
            "predicted_purchases": self.predicted_purchases,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "business_sector": self.business_sector,
            "department": self.department
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            project_id=data["project_id"],
            client_name=data["client_name"],
            brand_name=data["brand_name"],
            project_name=data["project_name"],
            pm_email=data["pm_email"],
            pd_email=data.get("pd_email"),
            cd_email=data.get("cd_email"),
            members=data.get("members"),
            status=data.get("status", "Proposal"),
            drive_folder_id=data.get("drive_folder_id"),
            spreadsheet_id=data.get("spreadsheet_id"),
            folder_ids=data.get("folder_ids"),
            predicted_sales=data.get("predicted_sales", 0.0),
            predicted_purchases=data.get("predicted_purchases", 0.0),
            period_start=data.get("period_start"),
            period_end=data.get("period_end"),
            business_sector=data.get("business_sector"),
            department=data.get("department")
        )

class WBSTask:
    def __init__(
        self,
        task_id: str,
        project_id: str,
        title: str,
        assigned_to: Optional[str] = None,
        start_date: Optional[str] = None,
        due_date: Optional[str] = None,
        status: str = "Waiting"
    ) -> None:
        self.task_id = task_id
        self.project_id = project_id
        self.title = title
        self.assigned_to = assigned_to
        self.start_date = start_date
        self.due_date = due_date
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "project_id": self.project_id,
            "title": self.title,
            "assigned_to": self.assigned_to,
            "start_date": self.start_date,
            "due_date": self.due_date,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WBSTask":
        return cls(
            task_id=data["task_id"],
            project_id=data["project_id"],
            title=data["title"],
            assigned_to=data.get("assigned_to"),
            start_date=data.get("start_date"),
            due_date=data.get("due_date"),
            status=data.get("status", "Waiting")
        )

class ResourceMM:
    def __init__(
        self,
        project_id: str,
        email: str,
        month: str,
        mm: float
    ) -> None:
        self.project_id = project_id
        self.email = email
        self.month = month
        self.mm = mm

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "email": self.email,
            "month": self.month,
            "mm": self.mm
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceMM":
        return cls(
            project_id=data["project_id"],
            email=data["email"],
            month=data["month"],
            mm=data["mm"]
        )
