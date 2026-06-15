from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Project:
    project_id: str
    client_name: str
    brand_name: str
    project_name: str
    pm_email: str
    importance: str  # "Standard" or "Critical"
    status: str      # "Proposal", "Execution", "Paused", "Lost", "Closure"
    pd_email: str    # Planning Director email
    cd_email: str    # Creative Director email
    pm_name: str
    pd_name: str
    cd_name: str
    members: List[str] = field(default_factory=list)
    drive_folder_id: Optional[str] = None
    spreadsheet_id: Optional[str] = None
    business_sector: str = "\uad11\uace0\uc0ac\uc5c5\ubd80\ubb38"
    department: str = "\uae30\ud68d1\ubcf8\ubd80"
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    predicted_sales: int = 1000000000
    predicted_purchases: str = "=C10*75%"
    step: int = 1                     # 1-11 advertising steps
    approval_status: str = "Pending"  # "Pending", "Approved", "Bypassed", "Rejected"
    lost_reason: Optional[str] = None
    ceo_approval_required: bool = False
    approved_at: Optional[str] = None
    temporary_deploy: bool = False
    created_at: Optional[str] = None  # ISO timestamp (e.g. "2026-06-15T15:12:00")

@dataclass
class WBSTask:
    task_id: str
    project_id: str
    name: str
    status: str       # "Pending", "In Progress", "Review Pending", "Approved"
    start_date: str
    end_date: str
    assignee: str

@dataclass
class ResourceMM:
    project_id: str
    employee_name: str
    role: str         # "Executive", "Director", "Senior", "Manager"
    mm_value: float   # Man-Month fraction (e.g. 0.5)
    days_input: float # Number of days input
    cost: float       # Calculated monthly cost based on role and mm_value

@dataclass
class AgentEntity:
    agent_id: str
    name: str
    role: str         # "Researcher", "AP_AE", "PD", "CD", "CW", "AD", "Designer", "Media"
    email: str
    budget: float = 0.0
    status: str = "Idle" # "Idle", "Active", "Offline"
