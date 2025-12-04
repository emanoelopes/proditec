# PRODITEC AVAMEC Automation System

This project is a comprehensive automation suite designed for the PRODITEC AVAMEC environment. It integrates various tools to streamline administrative tasks, including course management, participant tracking, and communication.

## Features

### 📊 Dashboard & Analytics
- **Web Application**: A Streamlit-based dashboard (`webapp/home.py`) provides visual insights into course data.
- **Evasion Tracking**: Monitor participant evasion rates and other key metrics.
- **Data Visualization**: Interactive charts using Plotly and Seaborn.

### 🤖 Automation Bots
- **WhatsApp Bot**: Automates communication via WhatsApp Web using Selenium (`bot_whatsapp`).
- **Google Meet Integration**: Automates meeting management and participant tracking (`meet`).
- **Avamec Automation**: Scripts to interact with the Avamec platform (`main.py`, `presencialidade`).

### 🛠️ Utilities
- **Spreadsheet Management**: Tools to process and verify registration spreadsheets (`planilha_inscricao.ipynb`, `verifica_inscricao.py`).
- **Email Verification**: Scripts to compare and validate email addresses (`src/compara_emails.py`).

## Getting Started

### Prerequisites
- Docker and Docker Compose (Recommended)
- Python 3.9+ (for local installation)
- Google Chrome (for Selenium-based bots)

### 🐳 Running with Docker

The easiest way to run the application is using Docker.

1.  **Build and Run the Web App:**
    ```bash
    docker-compose up --build
    ```
    Access the dashboard at `http://localhost:8501`.

2.  **Run Automation Scripts (Optional):**
    To run scripts that require a display (like the WhatsApp bot) inside Docker, you may need to configure Xvfb or run them locally. The `docker-compose.yml` includes a commented-out service for this purpose.

### 💻 Local Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd proditec
    ```

2.  **Install dependencies:**
    ```bash
    pip install .
    ```

3.  **Run the Web App:**
    ```bash
    streamlit run webapp/home.py
    ```

4.  **Run Automation Scripts:**
    Configure your `.env` file with necessary credentials (e.g., `AVAMEC_PASSWORD`).
    ```bash
    python main.py
    ```

## Project Structure

- `webapp/`: Streamlit dashboard application.
- `bot_whatsapp/`: WhatsApp automation scripts.
- `meet/`: Google Meet integration and monitoring.
- `src/`: General utility scripts.
- `Dockerfile`: Container configuration.
- `docker-compose.yml`: Service orchestration.

## License

[Add License Information Here]
