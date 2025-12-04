"""
Configurações do sistema de monitoramento de salas temáticas Google Meet.
"""
import os

# Configurações do Ollama
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Configurações do Google
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

# Scopes necessários para as APIs do Google
# Nota: Se o token.json já existe com scopes diferentes, pode ser necessário
# deletá-lo e autenticar novamente com os novos scopes
SCOPES = [
    'https://www.googleapis.com/auth/meetings.space.created',  # Para criar/listar espaços Meet
    'https://www.googleapis.com/auth/meetings.space.readonly',   # Para ler informações de espaços
    'https://www.googleapis.com/auth/spreadsheets.readonly',    # Para ler planilhas
    'https://www.googleapis.com/auth/calendar.readonly'         # Para ler eventos do calendário
]

# Configurações do Dashboard
DASHBOARD_REFRESH_INTERVAL = 30  # segundos
DASHBOARD_PORT = 8501

# Configurações da Planilha
# ID da planilha Google Sheets (será configurado via interface ou variável de ambiente)
SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID', '')
# Nome padrão da aba da planilha
DEFAULT_WORKSHEET_NAME = 'Turma-Grupo-Cursista-Zap'

# Configurações dos Grupos
NUM_GRUPOS = 10
TURMAS = ['A', 'B']

