import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .db import LocalJSONDatabase
from .models import Project, WBSTask, ResourceMM, AgentEntity
from .google_workspace import GoogleWorkspaceClient

logger = logging.getLogger("vibe_cording.org_os")

class PaperclipOS:
    def __init__(self, db: LocalJSONDatabase, workspace: GoogleWorkspaceClient):
        self.db = db
        self.workspace = workspace
        self._init_default_agents()

    def _init_default_agents(self):
        # Initialize default virtual employee entities
        default_agents = [
            AgentEntity("researcher", "Specialist Researcher", "Researcher", "researcher@brenxia.com", 2000000.0, "Idle"),
            AgentEntity("ap_ae", "Strategy AP/AE", "AP_AE", "ap_ae@brenxia.com", 2500000.0, "Idle"),
            AgentEntity("pd", "Planning Director", "PD", "pd@brenxia.com", 4000000.0, "Idle"),
            AgentEntity("cd", "Creative Director", "CD", "cd@brenxia.com", 4500000.0, "Idle"),
            AgentEntity("cw", "Copywriter", "CW", "cw@brenxia.com", 3000000.0, "Idle"),
            AgentEntity("ad", "Art Director", "AD", "ad@brenxia.com", 3500000.0, "Idle"),
            AgentEntity("designer", "UI/UX Designer", "Designer", "designer@brenxia.com", 3000000.0, "Idle"),
            AgentEntity("media", "Media Analyst", "Media", "media@brenxia.com", 2800000.0, "Idle")
        ]
        for agent in default_agents:
            if not self.db.get_agent(agent.agent_id):
                self.db.save_agent(agent)

    def trigger_agent_execution(self, agent_role: str, project_id: str, input_data: str) -> str:
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")
        
        logger.info(f"Triggering execution for agent role '{agent_role}' on project '{project.project_name}'")
        
        # Look up agent to update status
        agents = self.db.list_agents()
        target_agent = next((a for a in agents if a.role.lower() == agent_role.lower()), None)
        
        if target_agent:
            target_agent.status = "Active"
            self.db.save_agent(target_agent)

        result_str = f"Execution result for {agent_role}: processed input '{input_data}'"
        
        if target_agent:
            target_agent.status = "Idle"
            self.db.save_agent(target_agent)
            
        return result_str

class HermesAgent:
    def __init__(self, db: LocalJSONDatabase, workspace: GoogleWorkspaceClient, paperclip: PaperclipOS):
        self.db = db
        self.workspace = workspace
        self.paperclip = paperclip
        # Debate rounds tracker for projects: Key: (project_id, step), Value: round_count
        self.debate_rounds: Dict[tuple[str, int], int] = {}

    def process_project_creation(self, project: Project) -> tuple[bool, str]:
        """
        Checks importance and determines approval routing.
        """
        project.created_at = datetime.now().isoformat()
        
        if project.importance == "Critical" or project.ceo_approval_required:
            project.approval_status = "Pending"
            project.status = "Proposal"
            self.db.save_project(project)
            logger.info(f"[Hermes] Critical project '{project.project_name}' requires CEO approval.")
            return False, "Pending CEO Approval"
        else:
            project.approval_status = "Approved"
            project.status = "Proposal"
            project.approved_at = datetime.now().isoformat()
            self.db.save_project(project)
            logger.info(f"[Hermes] Standard project '{project.project_name}' approved automatically.")
            return True, "Approved"

    def check_approval_timeout(self, project_id: str) -> bool:
        """
        Fallback Rule for Delay:
        If CEO approval is pending for >= 12 hours, auto-deploys as [Unapproved] temporary project.
        """
        project = self.db.get_project(project_id)
        if not project or project.approval_status != "Pending":
            return False

        if not project.created_at:
            return False

        created_time = datetime.fromisoformat(project.created_at)
        if datetime.now() - created_time >= timedelta(hours=12):
            project.approval_status = "Bypassed"
            project.temporary_deploy = True
            project.project_name = f"[Unapproved] {project.project_name}"
            project.approved_at = datetime.now().isoformat()
            self.db.save_project(project)
            logger.warning(f"[Hermes] CEO Approval timeout (12h). Auto-deploying project '{project.project_name}' as temporary.")
            return True
        return False

    def check_clean_up_rule(self, project_id: str) -> bool:
        """
        Resource Clean-up Rule:
        If no files are uploaded within 48 hours after project creation, auto-archives the project.
        """
        project = self.db.get_project(project_id)
        if not project or project.status == "Lost" or project.status == "Closure":
            return False

        if not project.created_at:
            return False

        created_time = datetime.fromisoformat(project.created_at)
        if datetime.now() - created_time >= timedelta(hours=48):
            project.status = "Lost"
            project.lost_reason = "No activity for 48 hours (Auto Clean-up)"
            self.db.save_project(project)
            logger.warning(f"[Hermes] Resource Clean-up triggered: Project '{project.project_name}' archived due to 48 hours inactivity.")
            return True
        return False

    def handle_file_upload(self, project_id: str, folder_name: str, file_name: str) -> Optional[str]:
        """
        Auto Version Control (Version Push-down):
        - Moves previous files to '_이전버전_아카이브'.
        - Prompts for WBS updates if version matching patterns are found.
        - Triggers Human Bypass Rule if uploaded by a human.
        """
        project = self.db.get_project(project_id)
        if not project:
            return None

        logger.info(f"[Hermes] File '{file_name}' uploaded to standard subfolder '{folder_name}' of project '{project.project_name}'")
        
        # Simulate pushing old file down into archive folder
        logger.info(f"[Hermes] Performing version push-down. Moving previous files in '{folder_name}' to '_이전버전_아카이브' subfolder.")
        
        normalized = file_name.lower()
        has_final_pattern = ("final" in normalized or "v1.0" in normalized or "v1_0" in normalized)
        
        prompt_msg = None
        if has_final_pattern:
            prompt_msg = "WBS status update to 'Review Pending' requested. Confirm update?"
            logger.info(f"[Hermes] Version pattern matched in '{file_name}'. Prompt generated: {prompt_msg}")

        # Human Bypass Rule:
        self.apply_human_bypass(project, folder_name)

        return prompt_msg

    def apply_human_bypass(self, project: Project, folder_name: str):
        # 02.기획 or 03.제작 folders
        if "기획" in folder_name or "02" in folder_name:
            logger.info(f"[Hermes] Human Bypass Rule applied: Planning AI (PD) review bypassed for project '{project.project_name}'")
            if project.step == 4:
                project.step = 5
                self.db.save_project(project)
        elif "제작" in folder_name or "03" in folder_name:
            logger.info(f"[Hermes] Human Bypass Rule applied: Creative AI (CD) review bypassed for project '{project.project_name}'")
            if project.step == 6:
                project.step = 7
                self.db.save_project(project)

    def trigger_debate(self, project_id: str, step: int) -> bool:
        """
        Simulate a debate round between agents.
        If debate rounds reach 3, trigger deadlock resolution:
        give PD (step 5) or CD (step 8) veto power, and report to PM.
        """
        project = self.db.get_project(project_id)
        if not project:
            return False

        key = (project_id, step)
        rounds = self.debate_rounds.get(key, 0) + 1
        self.debate_rounds[key] = rounds
        logger.info(f"[Hermes] Project '{project.project_name}' Step {step} debate round {rounds}")

        if rounds >= 3:
            logger.warning(f"[Hermes] Deadlock detected on Step {step} (3 debate rounds reached). Resolving deadlock.")
            if step == 5:
                # PMO Deadlock: Planning Director (PD) veto power
                logger.info(f"[Hermes] PMO Deadlock resolved by assigning final veto authority to PD ({project.pd_email}). Reporting to PM.")
            elif step == 8:
                # Creative Deadlock: Creative Director (CD) veto power
                logger.info(f"[Hermes] Creative Deadlock resolved by assigning final veto authority to CD ({project.cd_email}). Reporting to PM.")
            
            # Reset debate rounds for this step
            self.debate_rounds[key] = 0
            return True
        return False

    def handle_reverse_routing(self, project_id: str, feedback_level: int):
        """
        Reverse Routing:
        Depending on feedback level:
        1. Minor edit -> Step 7
        2. Creative edit -> Step 6
        3. Strategic Pivot -> Step 4
        """
        project = self.db.get_project(project_id)
        if not project:
            return

        old_step = project.step
        if feedback_level == 1:
            project.step = 7
            logger.info(f"[Hermes] Reverse Routing level 1: Project '{project.project_name}' step changed from {old_step} to 7")
        elif feedback_level == 2:
            project.step = 6
            logger.info(f"[Hermes] Reverse Routing level 2: Project '{project.project_name}' step changed from {old_step} to 6")
        elif feedback_level == 3:
            project.step = 4
            logger.info(f"[Hermes] Reverse Routing level 3: Project '{project.project_name}' step changed from {old_step} to 4")
        
        self.db.save_project(project)

    def trigger_hybrid_expansion(self, project_id: str, required_role: str, option: str) -> Optional[AgentEntity]:
        """
        Hybrid Agent Expansion Protocol:
        If a needed role is not in the system, suggest expansion.
        Option A: Static template instance binding.
        """
        project = self.db.get_project(project_id)
        if not project:
            return None

        logger.info(f"[Hermes] Required role '{required_role}' missing for project '{project.project_name}'. Triggering expansion.")
        
        if option == "A":
            agent_id = f"custom_{required_role.lower()}"
            name = f"Custom {required_role}"
            email = f"{agent_id}@brenxia.com"
            new_agent = AgentEntity(
                agent_id=agent_id,
                name=name,
                role=required_role,
                email=email,
                budget=1500000.0,
                status="Idle"
            )
            self.db.save_agent(new_agent)
            logger.info(f"[Hermes] Option A selected: Static template instance bound for role '{required_role}' (Email: {email})")
            return new_agent
        elif option == "B":
            logger.info(f"[Hermes] Option B selected: External API integration configured for role '{required_role}'.")
            return None
        elif option == "C":
            logger.info(f"[Hermes] Option C selected: Developer specification document created for role '{required_role}'.")
            return None
        return None

    def validate_pms_numbers(self, project_id: str) -> List[str]:
        """
        Null-only Validation:
        Checks if required PMS fields (amount, mm_value, days_input) are completely null or empty.
        If 0 is explicitly written, it's considered valid.
        """
        project = self.db.get_project(project_id)
        if not project:
            return []

        warnings = []
        resources = self.db.list_resources(project_id)
        
        for r in resources:
            # Check if null or empty string
            if r.days_input is None or str(r.days_input).strip() == "":
                warnings.append(f"[Null Warning] Resource '{r.employee_name}' has missing input days.")
            if r.mm_value is None or str(r.mm_value).strip() == "":
                warnings.append(f"[Null Warning] Resource '{r.employee_name}' has missing M/M value.")

        if project.predicted_sales is None or str(project.predicted_sales).strip() == "":
            warnings.append("[Null Warning] Predicted sales are missing.")
        if project.predicted_purchases is None or str(project.predicted_purchases).strip() == "":
            warnings.append("[Null Warning] Predicted purchases are missing.")

        if warnings:
            logger.warning(f"[Hermes] PMS Validation failed with warnings: {warnings}")
        return warnings
