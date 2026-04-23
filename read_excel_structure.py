import pandas as pd
import sys

excel_file = "syncwith_sample_data/SyncWith Get Started 1.xlsx"

try:
    xl = pd.ExcelFile(excel_file)
    print(f"Sheets found: {xl.sheet_names}\n")
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=2)
        print(f"\n{sheet_name} Sheet:")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample data:")
        print(df.to_string(index=False))
        print("-" * 80)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
