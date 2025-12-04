# Google Sheets Automation

This script automates the creation of city-specific Google Sheets from a Master Spreadsheet.

## Prerequisites

1.  **Python 3**: Ensure Python is installed.
2.  **Google Cloud Project**:
    - Enable **Google Sheets API** and **Google Drive API**.
    - Create a **Service Account**.
    - Download the JSON key file and rename it to `service_account.json`.
    - **Important**: Share your Master Spreadsheet with the Service Account email address (found in the JSON file) so it can read it.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Configure the script (`automate_sheets.py`):
    - Open `automate_sheets.py`.
    - Update `MASTER_SPREADSHEET_ID` with the ID of your master sheet (found in the URL).
    - Update `CITIES_TAB_NAME` if your list of cities is in a different tab.
    - Update `CITY_COLUMN_INDEX` if the city names are not in the first column (Column A = 0).

3.  Place your `service_account.json` in this directory.

## Running the Script

```bash
python automate_sheets.py
```

## Notes

- The script will create a new spreadsheet for each city found in the list.
- It will rename the file to the City Name.
- It will update the cell in 'Status de confirmação de matrícula' (currently set to A1, change in script if needed).
- It will hide other tabs.
- It will restrict download/copy permissions for viewers.
- **IMPORTRANGE Permissions**: The script cannot automatically click "Allow Access" for `IMPORTRANGE` formulas. You may need to open each sheet once to approve access if the formulas break.

## Verification

If you have already created the sheets manually, you can use `verify_sheets.py` to check them.

1.  **Configure**: Open `verify_sheets.py` and update:
    - `CONTROL_SPREADSHEET_ID`: ID of your `controle_interno_ti` sheet.
    - `TARGET_FOLDER_ID`: ID of the folder containing the city sheets.
    - `CONTROL_TAB_NAME`: Name of the tab with the city list.
    - `CONTROL_CITY_COL_INDEX`: Column index (0 for A, 1 for B...) of the city names.

2.  **Run**:
    ```bash
    python verify_sheets.py
    ```

3.  **Report**: Check `verification_report.csv` for results.
