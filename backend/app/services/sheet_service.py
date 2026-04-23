import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any
from app.config import get_settings


class SheetService:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self._authenticate()

    def _authenticate(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.settings.google_credentials_path, scope
        )
        self.client = gspread.authorize(creds)

    def read_tab(self, tab_name: str) -> List[Dict[str, Any]]:
        sheet = self.client.open_by_key(self.settings.google_sheet_id)
        worksheet = sheet.worksheet(tab_name)
        return worksheet.get_all_records()
