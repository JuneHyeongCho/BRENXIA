import os
import logging
import requests
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .models import Project, ResourceMM

logger = logging.getLogger("vibe_cording.google_workspace")

class GoogleWorkspaceClient:
    def __init__(self, credentials_path: str, chat_webhook_url: Optional[str] = None, shared_drive_id: str = "root", is_mock: bool = True):
        self.credentials_path = credentials_path
        self.chat_webhook_url = chat_webhook_url
        self.shared_drive_id = shared_drive_id
        self.is_mock = is_mock
        self.drive_service = None
        self.sheets_service = None

        if self.is_mock:
            logger.info("Initializing GoogleWorkspaceClient in MOCK simulation mode.")
        else:
            logger.info(f"Initializing GoogleWorkspaceClient with credentials at: {credentials_path}")
            try:
                self._init_real_services()
                logger.info("Google API real services successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Google API real services: {e}. Falling back to MOCK mode.")
                self.is_mock = True

    def _init_real_services(self):
        # Setup Google OAuth Scopes
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        # Load credentials from JSON key file
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes
        )
        
        # Build API clients
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.sheets_service = build('sheets', 'v4', credentials=credentials)

    def _get_or_create_folder(self, name: str, parent_id: str) -> str:
        """
        Finds a folder by name under the specified parent.
        If it doesn't exist, creates it.
        """
        if self.is_mock:
            return f"mock_{name}_id"
            
        # Search query to find folder with the specific name and parent
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
        
        list_args = {
            'q': query,
            'spaces': 'drive',
            'fields': 'files(id, name)',
        }
        if self.shared_drive_id and self.shared_drive_id != "root":
            list_args['supportsAllDrives'] = True
            list_args['includeItemsFromAllDrives'] = True
            list_args['corpora'] = 'drive'
            list_args['driveId'] = self.shared_drive_id
            
        results = self.drive_service.files().list(**list_args).execute()
        files = results.get('files', [])
        
        if files:
            # Folder exists, return its ID
            folder_id = files[0]['id']
            logger.info(f"[REAL] Found existing folder '{name}' with ID '{folder_id}'")
            return folder_id
        else:
            # Folder doesn't exist, create it
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            create_args = {'body': metadata, 'fields': 'id'}
            if self.shared_drive_id and self.shared_drive_id != "root":
                create_args['supportsAllDrives'] = True
                
            file_obj = self.drive_service.files().create(**create_args).execute()
            folder_id = file_obj.get('id')
            logger.info(f"[REAL] Created folder '{name}' with ID '{folder_id}' under parent '{parent_id}'")
            return folder_id

    def create_project_folders(self, project: Project) -> Dict[str, str]:
        """
        Creates project directories on Google Drive:
        - Root: [YYMMDD]_[Client]_[Brand]_[ProjectName]
        - Subfolders: 00 to 05 standard subdirectories and their archives.
        """
        folder_names = [
            "00.Client_Materials",
            "01.Proposals",
            "02.Planning",
            "03.Production",
            "04.Media",
            "05.Administration",
            "06.PMS"
        ]
        
        simulated_ids = {}
        root_folder_name = f"260611_{project.client_name}_{project.brand_name}_{project.project_name}"
        
        # Determine parent folder based on "project/Year" hierarchy
        # We parse the year from "260611" prefix (first 2 digits)
        year_prefix = "26"
        if "_" in root_folder_name:
            prefix_part = root_folder_name.split("_")[0]
            if len(prefix_part) >= 2:
                year_prefix = prefix_part[:2]
        year_folder_name = f"20{year_prefix}"
        
        if self.is_mock:
            root_id = f"mock_root_id_{project.project_id}"
            simulated_ids["root"] = root_id
            logger.info(f"[MOCK] Created root folder '{root_folder_name}' under 'project/{year_folder_name}' with ID '{root_id}'")
            
            for folder in folder_names:
                sub_id = f"mock_{folder.lower()}_id"
                archive_id = f"mock_{folder.lower()}_archive_id"
                simulated_ids[folder] = sub_id
                simulated_ids[f"{folder}_archive"] = archive_id
                logger.info(f"[MOCK] Created subfolder '{folder}' (ID: {sub_id}) and '_previous_version_archive' (ID: {archive_id})")
        else:
            try:
                # 1. Traverse or create "project" folder under root shared drive
                project_folder_id = self._get_or_create_folder("project", self.shared_drive_id)
                
                # 2. Traverse or create year folder (e.g. "2026") under "project"
                year_folder_id = self._get_or_create_folder(year_folder_name, project_folder_id)
                
                # 3. Create root folder of the project under the year folder
                root_metadata = {
                    'name': root_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [year_folder_id]
                }
                
                create_args = {'body': root_metadata, 'fields': 'id'}
                if self.shared_drive_id and self.shared_drive_id != "root":
                    create_args['supportsAllDrives'] = True
                    
                file_obj = self.drive_service.files().create(**create_args).execute()
                root_id = file_obj.get('id')
                simulated_ids["root"] = root_id
                logger.info(f"[REAL] Created root folder '{root_folder_name}' with ID '{root_id}'")

                # 2. Create subfolders and internal archives
                for folder in folder_names:
                    sub_metadata = {
                        'name': folder,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [root_id]
                    }
                    sub_args = {'body': sub_metadata, 'fields': 'id'}
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        sub_args['supportsAllDrives'] = True
                        
                    sub_file = self.drive_service.files().create(**sub_args).execute()
                    sub_id = sub_file.get('id')
                    simulated_ids[folder] = sub_id
                    logger.info(f"[REAL] Created subfolder '{folder}' with ID '{sub_id}'")

                    # Create _previous_version_archive folder
                    archive_metadata = {
                        'name': '_previous_version_archive',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [sub_id]
                    }
                    archive_args = {'body': archive_metadata, 'fields': 'id'}
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        archive_args['supportsAllDrives'] = True
                        
                    archive_file = self.drive_service.files().create(**archive_args).execute()
                    archive_id = archive_file.get('id')
                    simulated_ids[f"{folder}_archive"] = archive_id
                    logger.info(f"[REAL] Created archive subfolder inside '{folder}' (ID: {archive_id})")
            except Exception as e:
                logger.error(f"Failed to create Google Drive folders: {e}")
                raise e
            
        return simulated_ids

    def sync_permissions(self, project: Project, folder_ids: Dict[str, str]) -> None:
        """
        Grants read/write permissions to members via Google Drive Permissions API.
        """
        if self.is_mock:
            logger.info(f"[MOCK] Syncing permissions for project '{project.project_name}'")
            logger.info(f"[MOCK] Granting full write access to PM: {project.pm_email}")
            logger.info(f"[MOCK] Granting write access to PD ({project.pd_email}) and CD ({project.cd_email})")
            for member in project.members:
                logger.info(f"[MOCK] Granting default write access to member: {member}")
        else:
            try:
                root_id = folder_ids.get("root")
                if not root_id:
                    return
                
                # Emails to share with
                emails = [project.pm_email, project.pd_email, project.cd_email] + project.members
                
                for email in set(emails):
                    if not email:
                        continue
                    try:
                        permission_metadata = {
                            'type': 'user',
                            'role': 'writer',
                            'emailAddress': email
                        }
                        permission_args = {
                            'fileId': root_id,
                            'body': permission_metadata
                        }
                        if self.shared_drive_id and self.shared_drive_id != "root":
                            permission_args['supportsAllDrives'] = True
                            
                        self.drive_service.permissions().create(**permission_args).execute()
                        logger.info(f"[REAL] Shared folder permission with user: {email}")
                    except Exception as invite_err:
                        logger.warning(f"[REAL] Failed to share folder permission with {email}: {invite_err}. Skipping.")
            except Exception as e:
                logger.error(f"Failed to sync Google Drive folder permissions: {e}")
                raise e

    def _build_pms_sheet_structure(self, spreadsheet_id: str, project: "Project") -> None:
        """
        Builds the PMS spreadsheet structure that exactly matches the company template.
        Template reference: https://docs.google.com/spreadsheets/d/1nnv1bV5bUfe-fjdJh8OWPQYdob0HBhttRgCDNjwHmPA

        Layout per tab (WPMS TOTAL DATABASE and each monthly tab):
          Row 1  : (empty)
          Row 2  : "Project Management Sheet" title
          Row 3-4: (empty)
          Row 5  : Project header line 1 — 고객사 / 프로젝트 / 프로젝트코드 / 최초작성일 / 프로젝트기간
          Row 6  : Project header line 2 — 사업부문 / 사업주관부서 / 기획책임자 / 제작책임자 / 비고
          Row 7  : (empty)
          Row 8  : "1. 사전예측" section header
          Row 9  : column headers (구분 / 총매출 / 총매입 / 순매출 / 내수율 / 투입인력 / 투입인력M/M / 투입원가 / 영업이익 / 영업이익율)
          Row 10 : 사전예측 values
          Row 11 : 현재 달성치
          Row 12 : 차액
          Row 13 : 목표 달성율
          Row 14 : (empty)
          Row 15 : "2. 월별 매출-매입 누적 종합"
          Row 16 : column headers (구분 / 1월..12월 / TOTAL)
          Rows 17-31: a.매출(총계/기획운영/제작/매체/기타) / b.매입(총계/..) / c.순매출(총계/..) / d.내수율
          Row 32 : (empty)
          Row 33 : "3. 월별 내부원가 현황"
          Row 34 : column headers
          Rows 35-46: f.투입인력 / g.투입M/M / h.산출가 (각각 총계/기획운영/제작/매체/기타)
          Row 47 : (empty)
          Row 48 : "4. 월별 영업이익 현황"
          Row 49 : column headers
          Rows 50-55: i.영업이익 / j.영업이익율 / k.인당평균영업이익 (각각 총계/기획운영/제작/매체/기타)
        """
        # ── Step 1: Create all tabs ──────────────────────────────────────────────
        tab_requests = [
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": 0, "title": "WPMS TOTAL DATABASE"},
                    "fields": "title"
                }
            }
        ]
        for m in range(1, 13):
            tab_requests.append({"addSheet": {"properties": {"title": f"{m}월"}}})
        tab_requests.append({"addSheet": {"properties": {"title": "OPT"}}})

        batch_resp = self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": tab_requests}
        ).execute()
        logger.info("[REAL] Created all PMS tabs.")

        # Collect sheetIds for formatting
        sheet_id_map: Dict[str, int] = {"WPMS TOTAL DATABASE": 0}
        for reply in batch_resp.get("replies", []):
            props = reply.get("addSheet", {}).get("properties", {})
            if props.get("title"):
                sheet_id_map[props["title"]] = props["sheetId"]

        # ── Helpers ───────────────────────────────────────────────────────────────
        # Column letters for months: D=1월 ... O=12월, P=TOTAL  (col B=index1, C=index2)
        month_cols = ["D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
        total_col = "P"

        def project_header_rows(tab: str) -> list:
            """Rows 1-7: title + project info block (same on every tab)."""
            return [
                [],                                                              # Row 1
                ["", "Project Management Sheet"],                                # Row 2
                [],                                                              # Row 3
                [],                                                              # Row 4
                [                                                                # Row 5
                    "", "고객사", project.client_name, "",
                    "프로젝트", project.project_name, "",
                    "프로젝트코드", f"BRX-{project.project_id[:8].upper()}", "",
                    "최초 작성일", "", "",
                    "프로젝트 기간", ""
                ],
                [                                                                # Row 6
                    "", "사업부문", "", "",
                    "사업주관부서", "", "",
                    "기획/운영 책임자", project.pd_email or "", "",
                    "제작 책임자", project.cd_email or "", "",
                    "비고", "-"
                ],
                [],                                                              # Row 7
            ]

        def month_col_header_row() -> list:
            """구분 / 1월 ~ 12월 / TOTAL"""
            return ["", "구분", "", "1월", "2월", "3월", "4월", "5월", "6월",
                    "7월", "8월", "9월", "10월", "11월", "12월", "TOTAL"]

        def sub_rows(label_b: str, label_c: str, tab: str, row_offset_d: int, is_total_db: bool) -> list:
            """
            Returns 5 rows for 총계/기획·운영/제작/매체/기타.
            For TOTAL DATABASE tab: all months filled.
            For monthly tabs: only the tab's own month column is filled, rest blank.
            is_total_db=True means we fill every month column with cross-tab SUMIF formulas.
            """
            sub_labels = ["총계", "기획/운영", "제작", "매체", "기타"]
            rows = []
            for i, sub in enumerate(sub_labels):
                b_cell = label_b if i == 0 else ""
                c_cell = sub
                row = ["", b_cell, c_cell]
                for _ in range(12):
                    row.append("")   # placeholder — filled below
                row.append("")       # TOTAL placeholder
                rows.append(row)
            return rows

        # ── Step 2: Build content for WPMS TOTAL DATABASE ────────────────────────
        # For the database tab every cell references the corresponding monthly tab.
        def total_db_cross_ref(monthly_row_index: int, col: str, month_num: int) -> str:
            """Returns a cross-sheet reference for the total DB tab."""
            return f"='{month_num}월'!{col}{monthly_row_index}"

        # We pre-define absolute row positions on a monthly tab (1-indexed):
        # Row 10 = 사전예측 data
        # Row 11 = 현재달성치
        # Row 17 = a.매출 총계,  18=기획/운영, 19=제작, 20=매체, 21=기타
        # Row 22 = b.매입 총계,  23=기획/운영, 24=제작, 25=매체, 26=기타
        # Row 27 = c.순매출 총계, 28=기획/운영, 29=제작, 30=매체, 31=기타
        # Row 32 = d.내수율
        # Row 35 = f.투입인력 총계, 36=기획/운영, 37=제작, 38=매체, 39=기타
        # Row 40 = g.투입M/M 총계, 41=기획/운영, 42=제작, 43=매체, 44=기타
        # Row 45 = h.산출가 총계,  46=기획/운영, 47=제작, 48=매체, 49=기타
        # Row 51 = i.영업이익 총계, 52=기획/운영, 53=제작, 54=매체, 55=기타
        # Row 56 = j.영업이익율
        # Row 57 = k.인당평균영업이익

        def build_tab_values(is_total_db: bool, month_num: int = 0) -> list:
            """
            Builds the full row list for one tab with proper Sheets formulas.

            Fixed row map (1-indexed, same on every tab):
              1-7   : project header block
              8     : "1. 사전예측" section title
              9     : Section-1 column header row
              10    : 사전예측 (manual)
              11    : 현재 달성치  (formula → pulls from sections 2/3/4)
              12    : 차액         (formula = row11 - row10)
              13    : 목표달성율   (formula = row11 / row10)
              14    : (blank)
              15    : "2. 월별 매출-매입 누적 종합"
              16    : month column header row
              17    : a.매출  총계       (formula = SUM of sub-rows)
              18    : a.매출  기획/운영  (manual / cross-ref for total_db)
              19    : a.매출  제작
              20    : a.매출  매체
              21    : a.매출  기타
              22    : b.매입  총계       (formula)
              23-26 : b.매입  sub-rows
              27    : c.순매출 총계      (formula = row17 - row22 per column)
              28-31 : c.순매출 sub-rows  (formula = a_sub - b_sub per column)
              32    : d.내수율           (formula = IFERROR(c/a))
              33    : (blank)
              34    : "3. 월별 내부원가 현황"
              35    : month column header row
              36    : f.투입인력 총계    (formula)
              37-40 : f.투입인력 sub-rows
              41    : g.투입M/M 총계     (formula)
              42-45 : g.투입M/M sub-rows
              46    : h.산출가 총계      (formula)
              47-50 : h.산출가 sub-rows  (manual – depends on head-count/grade)
              51    : (blank)
              52    : "4. 월별 영업이익 현황"
              53    : month column header row
              54    : i.영업이익 총계    (formula = row27 - row46 per column)
              55-58 : i.영업이익 sub-rows(formula = c_sub - h_sub)
              59    : j.영업이익율       (formula = IFERROR(i/a))
              60    : k.인당평균영업이익 (formula = IFERROR(i/f))
            """
            # mc: the data column for this tab's month in sections 2/3/4
            # TOTAL DATABASE  → "P" (the TOTAL column aggregating all months)
            # Monthly tab m   → month_cols[m-1]  (D for Jan, E for Feb, …)
            mc = "P" if is_total_db else month_cols[month_num - 1]

            rows = project_header_rows("TOTAL DB" if is_total_db else f"{month_num}월")

            # ── Section 1: 사전예측 (rows 8-13) ───────────────────────────────
            rows.append(["", "1. 사전예측"])                                       # Row 8
            rows.append([                                                           # Row 9
                "", "구분", "총매출", "", "총매입", "", "순매출", "",
                "내수율", "투입인력", "투입인력M/M", "투입원가", "", "영업이익", "", "영업이익율"
            ])
            rows.append(["", "사전예측"] + [""] * 14)                              # Row 10 – manual

            # Row 11: 현재 달성치 — references section 2/3/4 cells
            rows.append([
                "", "현재 달성치",
                f"={mc}17", "",           # 총매출  ← a.매출 총계
                f"={mc}22", "",           # 총매입  ← b.매입 총계
                f"={mc}27", "",           # 순매출  ← c.순매출 총계
                f"=IFERROR({mc}32,\"\")", # 내수율  ← d.내수율
                f"={mc}36",              # 투입인력 ← f.투입인력 총계
                f"={mc}41",              # 투입M/M  ← g.투입M/M 총계
                f"={mc}46", "",           # 투입원가 ← h.산출가 총계
                f"={mc}54", "",           # 영업이익 ← i.영업이익 총계
                f"=IFERROR({mc}59,\"\")", # 영업이익율 ← j.영업이익율
            ])
            # Row 12: 차액 = 현재달성치 - 사전예측
            rows.append([
                "", "차액",
                "=C11-C10", "", "=E11-E10", "", "=G11-G10", "",
                "", "=J11-J10", "=K11-K10", "=L11-L10", "",
                "=N11-N10", "", ""
            ])
            # Row 13: 목표달성율 = 현재달성치 / 사전예측
            rows.append([
                "", "목표 달성율",
                "=IFERROR(C11/C10,\"\")", "", "=IFERROR(E11/E10,\"\")", "",
                "=IFERROR(G11/G10,\"\")", "", "", "=IFERROR(J11/J10,\"\")",
                "", "=IFERROR(L11/L10,\"\")", "",
                "=IFERROR(N11/N10,\"\")", "", ""
            ])
            rows.append([])                                                         # Row 14

            # ── Section 2: 월별 매출-매입 누적 종합 (rows 15-32) ──────────────
            rows.append(["", "2. 월별 매출-매입 누적 종합"])                       # Row 15
            rows.append(month_col_header_row())                                    # Row 16

            # Helper: build a row with 12-column formulas + TOTAL column
            def data_row(b, c, col_formulas: list, total_formula: str) -> list:
                return ["", b, c] + col_formulas + [total_formula]

            # ── a.매출 (rows 17-21) ──
            # Row 17: a.매출 총계
            if is_total_db:
                rows.append(data_row("a.매출", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}17" for mn in range(1, 13)],
                    "=SUM(D17:O17)"))
            else:
                rows.append(data_row("a.매출", "총계",
                    [f"=SUM({col}18:{col}21)" for col in month_cols],
                    "=SUM(D17:O17)"))
            # Rows 18-21: sub-rows (manual for monthly tabs)
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 18 + i
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub, [""] * 12, f"=SUM(D{r}:O{r})"))

            # ── b.매입 (rows 22-26) ──
            # Row 22: b.매입 총계
            if is_total_db:
                rows.append(data_row("b.매입", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}22" for mn in range(1, 13)],
                    "=SUM(D22:O22)"))
            else:
                rows.append(data_row("b.매입", "총계",
                    [f"=SUM({col}23:{col}26)" for col in month_cols],
                    "=SUM(D22:O22)"))
            # Rows 23-26: sub-rows
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 23 + i
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub, [""] * 12, f"=SUM(D{r}:O{r})"))

            # ── c.순매출 = a - b (rows 27-31) ──
            # Row 27: 총계
            if is_total_db:
                rows.append(data_row("c.순매출\n(a-b)", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}27" for mn in range(1, 13)],
                    "=SUM(D27:O27)"))
            else:
                rows.append(data_row("c.순매출\n(a-b)", "총계",
                    [f"={col}17-{col}22" for col in month_cols],
                    "=SUM(D27:O27)"))
            # Rows 28-31: sub-rows (derived from a_sub - b_sub)
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 28 + i
                a_r = 18 + i   # a.매출 sub
                b_r = 23 + i   # b.매입 sub
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub,
                        [f"={col}{a_r}-{col}{b_r}" for col in month_cols],
                        f"=SUM(D{r}:O{r})"))

            # ── d.내수율 = c/a (row 32) ──
            if is_total_db:
                rows.append(data_row("d.내수율(c/a)", "",
                    [f"='{mn}월'!{month_cols[mn-1]}32" for mn in range(1, 13)],
                    "=IFERROR(P27/P17,\"\")"))
            else:
                rows.append(data_row("d.내수율(c/a)", "",
                    [f"=IFERROR({col}27/{col}17,\"\")" for col in month_cols],
                    "=IFERROR(P27/P17,\"\")"))

            rows.append([])  # Row 33 separator

            # ── Section 3: 월별 내부원가 현황 (rows 34-50) ────────────────────
            rows.append(["", "3. 월별 내부원가 현황"])                             # Row 34
            rows.append(month_col_header_row())                                    # Row 35

            # ── f.투입인력 (rows 36-40) ──
            if is_total_db:
                rows.append(data_row("f.투입 인력", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}36" for mn in range(1, 13)],
                    "=SUM(D36:O36)"))
            else:
                rows.append(data_row("f.투입 인력", "총계",
                    [f"=SUM({col}37:{col}40)" for col in month_cols],
                    "=SUM(D36:O36)"))
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 37 + i
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub, [""] * 12, f"=SUM(D{r}:O{r})"))

            # ── g.투입M/M (rows 41-45) ──
            if is_total_db:
                rows.append(data_row("g.투입 M/M", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}41" for mn in range(1, 13)],
                    "=SUM(D41:O41)"))
            else:
                rows.append(data_row("g.투입 M/M", "총계",
                    [f"=SUM({col}42:{col}45)" for col in month_cols],
                    "=SUM(D41:O41)"))
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 42 + i
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub, [""] * 12, f"=SUM(D{r}:O{r})"))

            # ── h.산출가 (rows 46-50) ──
            # 산출가 = 투입M/M × 직위 단가 (complex per-person calc → sub-rows manual)
            if is_total_db:
                rows.append(data_row("h.산출가", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}46" for mn in range(1, 13)],
                    "=SUM(D46:O46)"))
            else:
                rows.append(data_row("h.산출가", "총계",
                    [f"=SUM({col}47:{col}50)" for col in month_cols],
                    "=SUM(D46:O46)"))
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 47 + i
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub, [""] * 12, f"=SUM(D{r}:O{r})"))

            rows.append([])   # Row 51 separator

            # ── Section 4: 월별 영업이익 현황 (rows 52-60) ───────────────────
            rows.append(["", "4. 월별 영업이익 현황"])                             # Row 52
            rows.append(month_col_header_row())                                    # Row 53

            # ── i.영업이익 = c(순매출) - h(산출가) (rows 54-58) ──
            # Row 54: i.영업이익 총계
            if is_total_db:
                rows.append(data_row("i.영업이익\n(c-h)", "총계",
                    [f"='{mn}월'!{month_cols[mn-1]}54" for mn in range(1, 13)],
                    "=SUM(D54:O54)"))
            else:
                rows.append(data_row("i.영업이익\n(c-h)", "총계",
                    [f"={col}27-{col}46" for col in month_cols],
                    "=SUM(D54:O54)"))
            # Rows 55-58: sub-rows (c_sub - h_sub)
            for i, sub in enumerate(["기획/운영", "제작", "매체", "기타"]):
                r = 55 + i
                c_r = 28 + i   # c.순매출 sub
                h_r = 47 + i   # h.산출가 sub
                if is_total_db:
                    rows.append(data_row("", sub,
                        [f"='{mn}월'!{month_cols[mn-1]}{r}" for mn in range(1, 13)],
                        f"=SUM(D{r}:O{r})"))
                else:
                    rows.append(data_row("", sub,
                        [f"={col}{c_r}-{col}{h_r}" for col in month_cols],
                        f"=SUM(D{r}:O{r})"))

            # ── j.영업이익율 = i/a (row 59) ──
            if is_total_db:
                rows.append(data_row("j.영업이익율(i/a)", "",
                    [f"='{mn}월'!{month_cols[mn-1]}59" for mn in range(1, 13)],
                    "=IFERROR(P54/P17,\"\")"))
            else:
                rows.append(data_row("j.영업이익율(i/a)", "",
                    [f"=IFERROR({col}54/{col}17,\"\")" for col in month_cols],
                    "=IFERROR(P54/P17,\"\")"))

            # ── k.인당평균영업이익 = i/f (row 60) ──
            if is_total_db:
                rows.append(data_row("k.인당 평균 영업이익(i/f)", "",
                    [f"='{mn}월'!{month_cols[mn-1]}60" for mn in range(1, 13)],
                    "=IFERROR(P54/P36,\"\")"))
            else:
                rows.append(data_row("k.인당 평균 영업이익(i/f)", "",
                    [f"=IFERROR({col}54/{col}36,\"\")" for col in month_cols],
                    "=IFERROR(P54/P36,\"\")"))

            return rows



        # ── Step 3: Batch write ───────────────────────────────────────────────────
        value_data = [
            {
                "range": "WPMS TOTAL DATABASE!A1",
                "values": build_tab_values(is_total_db=True),
            }
        ]
        for m in range(1, 13):
            value_data.append({
                "range": f"'{m}월'!A1",
                "values": build_tab_values(is_total_db=False, month_num=m),
            })

        # OPT tab — unit costs from the actual template
        opt_values = [
            [],
            [],
            [],
            ["", "직위", "단가"],
            ["", "임원", 8451914],
            ["", "수석M", 6353006],
            ["", "책임M", 4986758],
            ["", "선임M", 4486165],
            ["", "매니저", 4042272],
        ]
        value_data.append({"range": "OPT!A1", "values": opt_values})

        self.sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"valueInputOption": "USER_ENTERED", "data": value_data},
        ).execute()
        logger.info("[REAL] Populated full PMS structure matching company template.")

        # ── Step 4: Formatting ────────────────────────────────────────────────────
        fmt_requests = []
        bg_dark    = {"red": 0.18, "green": 0.18, "blue": 0.35}
        bg_section = {"red": 0.85, "green": 0.90, "blue": 1.0}
        bg_sub     = {"red": 0.95, "green": 0.95, "blue": 1.0}
        white      = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
        black      = {"red": 0.0,  "green": 0.0,  "blue": 0.0}

        def fmt_row(sheet_id: int, row_0: int, cols: int,
                    bg: dict, text_color: dict = None, bold: bool = True) -> dict:
            cell_fmt: Dict[str, Any] = {
                "backgroundColor": bg,
                "textFormat": {"bold": bold, "foregroundColor": text_color or black},
            }
            return {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_0, "endRowIndex": row_0 + 1,
                        "startColumnIndex": 0,  "endColumnIndex": cols,
                    },
                    "cell": {"userEnteredFormat": cell_fmt},
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            }

        for tab_title, sid in sheet_id_map.items():
            if tab_title == "OPT":
                continue
            # Row 2 (index 1) — title row dark
            fmt_requests.append(fmt_row(sid, 1, 16, bg_dark, white))
            # Row 5 (index 4) — project header 1
            fmt_requests.append(fmt_row(sid, 4, 16, bg_section))
            # Row 6 (index 5) — project header 2
            fmt_requests.append(fmt_row(sid, 5, 16, bg_section))
            # Row 8 (index 7) — section 1 header
            fmt_requests.append(fmt_row(sid, 7, 16, bg_dark, white))
            # Row 9 (index 8) — column headers for section 1
            fmt_requests.append(fmt_row(sid, 8, 16, bg_section))
            # Row 15 (index 14) — section 2 header
            fmt_requests.append(fmt_row(sid, 14, 16, bg_dark, white))
            # Row 16 (index 15) — month column headers
            fmt_requests.append(fmt_row(sid, 15, 16, bg_section))
            # Section 3 header (row 34 = index 33 after blank row 33)
            fmt_requests.append(fmt_row(sid, 33, 16, bg_dark, white))
            fmt_requests.append(fmt_row(sid, 34, 16, bg_section))
            # Section 4 header
            fmt_requests.append(fmt_row(sid, 47, 16, bg_dark, white))
            fmt_requests.append(fmt_row(sid, 48, 16, bg_section))

        # OPT tab header
        opt_sid = sheet_id_map.get("OPT")
        if opt_sid:
            fmt_requests.append(fmt_row(opt_sid, 3, 3, bg_dark, white))

        if fmt_requests:
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": fmt_requests},
            ).execute()
            logger.info("[REAL] Applied formatting to PMS sheet headers.")



    def setup_pms_spreadsheet(self, project: Project, pms_folder_id: str) -> str:
        """
        Checks if a PMS spreadsheet already exists for this project inside the 06.PMS folder,
        and copies the master template if not.
        Returns the spreadsheet ID.
        """
        spreadsheet_name = f"BRENXIA WPMS_{project.client_name}_{project.project_name}"

        if self.is_mock:
            return f"mock_spreadsheet_id_{project.project_id}"

        try:
            # 1. Check if BRENXIA WPMS_[ClientName]_[ProjectName] exists inside 06.PMS folder
            query = f"name = '{spreadsheet_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and '{pms_folder_id}' in parents and trashed = false"
            
            list_args = {
                'q': query,
                'spaces': 'drive',
                'fields': 'files(id, name)',
            }
            if self.shared_drive_id and self.shared_drive_id != "root":
                list_args['supportsAllDrives'] = True
                list_args['includeItemsFromAllDrives'] = True
                list_args['corpora'] = 'drive'
                list_args['driveId'] = self.shared_drive_id
                
            results = self.drive_service.files().list(**list_args).execute()
            files = results.get('files', [])
            
            if files:
                spreadsheet_id = files[0]['id']
                logger.info(f"[REAL] Found existing PMS Spreadsheet '{spreadsheet_name}' with ID '{spreadsheet_id}'")
                return spreadsheet_id
                
            # 2. Attempt to copy a master template spreadsheet if configured
            template_id = os.environ.get("WPMS_TEMPLATE_ID", "")
            spreadsheet_id = None
            
            if template_id:
                try:
                    body = {'name': spreadsheet_name, 'parents': [pms_folder_id]}
                    copy_args = {'fileId': template_id, 'body': body, 'fields': 'id'}
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        copy_args['supportsAllDrives'] = True
                    copied_file = self.drive_service.files().copy(**copy_args).execute()
                    spreadsheet_id = copied_file.get('id')
                    logger.info(f"[REAL] Created PMS Spreadsheet from template '{template_id}'. ID: {spreadsheet_id}")
                except Exception as copy_err:
                    logger.warning(f"[REAL] Failed to copy template '{template_id}': {copy_err}. Creating from scratch.")

            if not spreadsheet_id:
                # 3. Create a fresh blank spreadsheet
                metadata = {
                    'name': spreadsheet_name,
                    'mimeType': 'application/vnd.google-apps.spreadsheet',
                    'parents': [pms_folder_id]
                }
                create_args = {'body': metadata, 'fields': 'id'}
                if self.shared_drive_id and self.shared_drive_id != "root":
                    create_args['supportsAllDrives'] = True
                new_sheet = self.drive_service.files().create(**create_args).execute()
                spreadsheet_id = new_sheet.get('id')
                logger.info(f"[REAL] Created blank PMS Spreadsheet '{spreadsheet_name}'. ID: {spreadsheet_id}")

                # 4. Build the full PMS structure (tabs + headers + formulas + formatting)
                self._build_pms_sheet_structure(spreadsheet_id, project)

            return spreadsheet_id
        except Exception as e:
            logger.error(f"Failed to setup PMS spreadsheet: {e}")
            raise e

    def sync_pms_permissions(self, project: Project, spreadsheet_id: str) -> None:
        """
        Grants read/write permissions to PD/CD and read-only to PM/members on PMS Spreadsheet.
        """
        if self.is_mock:
            logger.info(f"[MOCK] Syncing PMS permissions for spreadsheet '{spreadsheet_id}'")
            logger.info(f"[MOCK] Granting write access to PD ({project.pd_email}) and CD ({project.cd_email})")
            logger.info(f"[MOCK] Granting read-only access to PM ({project.pm_email}) and members: {project.members}")
            return

        try:
            # 1. PD and CD get 'writer' role
            writers = set(filter(None, [project.pd_email, project.cd_email]))
            for email in writers:
                try:
                    permission_metadata = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    permission_args = {
                        'fileId': spreadsheet_id,
                        'body': permission_metadata
                    }
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        permission_args['supportsAllDrives'] = True
                    self.drive_service.permissions().create(**permission_args).execute()
                    logger.info(f"[REAL] Shared PMS writer permission with: {email}")
                except Exception as err:
                    logger.warning(f"[REAL] Failed to share PMS writer permission with {email}: {err}. Skipping.")

            # 2. PM and members get 'reader' role
            readers = set(filter(None, [project.pm_email] + project.members)) - writers
            for email in readers:
                try:
                    permission_metadata = {
                        'type': 'user',
                        'role': 'reader',
                        'emailAddress': email
                    }
                    permission_args = {
                        'fileId': spreadsheet_id,
                        'body': permission_metadata
                    }
                    if self.shared_drive_id and self.shared_drive_id != "root":
                        permission_args['supportsAllDrives'] = True
                    self.drive_service.permissions().create(**permission_args).execute()
                    logger.info(f"[REAL] Shared PMS reader permission with: {email}")
                except Exception as err:
                    logger.warning(f"[REAL] Failed to share PMS reader permission with {email}: {err}. Skipping.")
        except Exception as e:
            logger.error(f"Failed to sync PMS spreadsheet permissions: {e}")
            raise e

    def get_mm_unit_cost(self, role: str) -> float:
        """
        Simulates looking up employee unit cost.
        """
        costs = {
            "Executive": 10000.0,
            "Director": 8000.0,
            "Senior": 6000.0,
            "Manager": 4000.0
        }
        return costs.get(role, 3000.0)

    def write_pms_row(self, project: Project, month: int, row_data: Dict[str, Any]) -> None:
        """
        Writes project financials and M/M allocation values into client's WPMS Spreadsheet.
        """
        spreadsheet_name = f"BRENXIA WPMS_{project.client_name}.gsheet"
        if self.is_mock:
            logger.info(f"[MOCK] Writing row to '{spreadsheet_name}', Tab: '{month} Month'")
            logger.info(f"[MOCK] Row data: {row_data}")
        else:
            try:
                if not project.spreadsheet_id:
                    logger.warning("No spreadsheet ID defined on project object. Cannot write row.")
                    return
                
                sheet_range = f"'{month}월'!A:J"
                values = [list(row_data.values())]
                
                body = {
                    'values': values
                }
                
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=project.spreadsheet_id,
                    range=sheet_range,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                logger.info(f"[REAL] Successfully appended row data to Google Sheet '{project.spreadsheet_id}'")
            except Exception as e:
                logger.error(f"Failed to write row data to Google Sheets: {e}")
                raise e

    def check_essential_financial_fields(self, project: Project, month: int, records: List[Dict[str, Any]]) -> List[str]:
        """
        Validates that billing/cost values are present. Null/empty triggers alert. 0 is accepted.
        """
        missing_fields = []
        for index, record in enumerate(records):
            for field_name, value in record.items():
                if value is None or str(value).strip() == "":
                    missing_fields.append(f"Row {index + 1}: Field '{field_name}' is empty.")
        return missing_fields

    def send_google_chat_card(self, space_id: str, title: str, subtitle: str, buttons: List[Dict[str, str]]) -> None:
        """
        Sends an interactive Google Chat card with buttons via Incoming Webhook.
        """
        if self.is_mock:
            logger.info(f"[MOCK] Sending Google Chat card to space '{space_id}'")
            logger.info(f"[MOCK] Card Title: {title} | Subtitle: {subtitle}")
            for btn in buttons:
                logger.info(f"[MOCK] Card Button -> Label: {btn.get('label')}, Action: {btn.get('action')}")
        else:
            if not self.chat_webhook_url:
                logger.warning("No chat webhook URL configured. Cannot send Google Chat notification card.")
                return
            
            # Formulate Google Chat interactive card JSON structure
            card_widgets = []
            for btn in buttons:
                card_widgets.append({
                    "button": {
                        "textButton": {
                            "text": btn.get("label", "Action"),
                            "onClick": {
                                "action": {
                                    "actionMethodName": btn.get("action", "unknown")
                                }
                            }
                        }
                    }
                })

            card_body = {
                "cards": [
                    {
                        "header": {
                            "title": title,
                            "subtitle": subtitle
                        },
                        "sections": [
                            {
                                "widgets": card_widgets
                            }
                        ]
                    }
                ]
            }

            try:
                response = requests.post(self.chat_webhook_url, json=card_body)
                if response.status_code == 200:
                    logger.info("[REAL] Successfully sent Google Chat notification card via Incoming Webhook.")
                else:
                    logger.error(f"[REAL] Google Chat Webhook returned status code: {response.status_code}, response: {response.text}")
            except Exception as e:
                logger.error(f"Failed to post notification message to Google Chat webhook: {e}")
