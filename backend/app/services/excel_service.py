import pandas as pd
from typing import List, Dict, Any
from pathlib import Path


class ExcelService:
    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or "/app/syncwith_sample_data/SyncWith Get Started 1.xlsx"

    def read_tab(self, tab_name: str) -> List[Dict[str, Any]]:
        """Read data from an Excel sheet tab"""
        df = pd.read_excel(self.excel_path, sheet_name=tab_name)
        return df.to_dict('records')
