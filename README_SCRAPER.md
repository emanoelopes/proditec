# Avamec Scraper

This script scrapes student grades from the Avamec platform.

## Prerequisites

1.  **Python 3.10+**
2.  **Google Chrome** installed.
3.  **Dependencies**: Install via `pip install -r requirements.txt`.

## Configuration

1.  Ensure you have a `.env` file in the project directory with your credentials:
    ```env
    AVAMEC_USER=your_username
    AVAMEC_PASSWORD=your_password
    ```

## Usage

Run the scraper:

```bash
python3 avamec_scraper.py
```

## Important Note on reCAPTCHA

The Avamec login page uses reCAPTCHA, which may block automated login attempts.

-   **If running locally (with a visible browser):** The script will wait for you to solve the CAPTCHA if detected.
-   **If running headless (server/background):** Login will likely fail. You may need to run the script in a desktop environment first to establish a session or solve the CAPTCHA manually.

## Output

The script will generate JSON files for each activity scraped, e.g., `grades_179_0.json`.
The JSON format is:
```json
[
  {
    "name": "Student Name",
    "grades": ["10", "8", "", "10", "9"]
  },
  ...
]
```
