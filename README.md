# Sistema de Automação Proditec

Sistema para automação de coleta e análise de dados do Avamec e Google Sheets.

## Estrutura do Projeto

* `src/`: Código fonte da aplicação
  * `src/core/`: Lógica principal de raspagem e processamento
  * `src/services/`: Integrações com APIs externas (Google, etc)
  * `src/utils/`: Utilitários gerais
* `config/`: Arquivos de configuração e credenciais
* `data/`: Dados gerados e arquivos de entrada (ignorados no git)
* `scripts/`: Scripts utilitários diversos
* `locales/`: Arquivos de tradução (i18n)

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual: `python3 -m venv .venv`
3. Ative o ambiente: `source .venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Configure o arquivo `.env` (use `.env.example` como base)
6. Coloque as credenciais do Google em `config/credentials.json` e `config/token.json` (se existir)

## Como Usar

### Executar a Aplicação Principal

```bash
# Executar scraper básico (Turma B)
python -m src.main --scraper basic

# Executar scraper completo (Turma A e B, todos os grupos)
python -m src.main --scraper full

# Mudar idioma para Inglês
python -m src.main --lang en
```

### Scripts Utilitários

```bash
# Baixar planilhas do Google (Selenium)
python scripts/download_sheets_selenium.py

# Consolidar dados baixados
python src/core/consolidate_grades.py
```

## Docker

Para construir e rodar via Docker:

```bash
docker-compose build
docker-compose up
```
