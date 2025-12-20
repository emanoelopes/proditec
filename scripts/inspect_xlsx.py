import pandas as pd

def inspect_xlsx():
    file_path = '/home/emanoel/proditec/performance_data.xlsx'
    try:
        # Load the Excel file specifically to list sheet names first
        xl = pd.ExcelFile(file_path)
        print(f"Sheet names found: {len(xl.sheet_names)}")
        print(xl.sheet_names)
        
        # Read the first sheet to check columns
        if xl.sheet_names:
            first_sheet = xl.sheet_names[0]
            print(f"\n--- Inspecting first sheet: {first_sheet} ---")
            df = pd.read_excel(file_path, sheet_name=first_sheet)
            print("Columns:", df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3).to_string())
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == '__main__':
    inspect_xlsx()
