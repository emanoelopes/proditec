# 📊 Agente de Monitoramento de Salas Temáticas - Google Meet

Sistema Python com dashboard Streamlit em tempo real para monitorar e validar que todos os cursistas e ATTs estão nas salas temáticas corretas durante encontros síncronos, usando modelos locais via Ollama API para análise inteligente.

## 🎯 Funcionalidades

- **Monitoramento em Tempo Real**: Acompanhamento de participantes em cada sala temática
- **Integração Google**: Leitura de planilhas Google Sheets e acesso à Google Meet API
- **Análise Inteligente**: Agente de IA usando Ollama para análise de discrepâncias e recomendações
- **Dashboard Interativo**: Interface Streamlit com visualizações e métricas
- **Filtro por Turma**: Visualização separada para Turma A e Turma B
- **Alertas e Recomendações**: Identificação automática de problemas e sugestões de ações

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta Google com acesso às APIs:
  - Google Sheets API
  - Google Meet API
  - Google Calendar API (necessária para busca automática de meetings)
- Ollama instalado e rodando localmente (para o agente de IA)
- Credenciais OAuth2 do Google (arquivo `credentials.json`)

### ⚙️ Habilitar APIs no Google Cloud Console

Antes de usar, você precisa habilitar as seguintes APIs no Google Cloud Console:

1. **Google Sheets API**: https://console.cloud.google.com/apis/library/sheets.googleapis.com
2. **Google Meet API**: https://console.cloud.google.com/apis/library/meet.googleapis.com
3. **Google Calendar API**: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

**Projeto**: 133165406108

Após habilitar, aguarde alguns minutos para a propagação.

## 🛠️ Instalação

1. **Clone ou navegue até o diretório**:
   ```bash
   cd /home/emanoel/progpy/avamec/meet
   ```

2. **Crie um ambiente virtual (recomendado)**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais do Google**:
   - Baixe o arquivo `credentials.json` do Google Cloud Console
   - Coloque o arquivo no diretório `meet/`
   - Execute o dashboard pela primeira vez - ele solicitará autenticação automaticamente
   - **Importante**: Autorize TODOS os scopes solicitados no navegador:
     - Google Meet API
     - Google Sheets API (readonly)
     - Google Calendar API (readonly)
   
   **Se você já tem um `token.json` antigo** (por exemplo, do `quickstart.py`), pode precisar deletá-lo:
   ```bash
   rm token.json
   # ou use o script auxiliar:
   ./reset_auth.sh
   ```
   
   Depois, execute o dashboard novamente para reautenticar com todos os scopes necessários.

5. **Configure o Ollama** (opcional, mas recomendado):
   - Instale o Ollama: https://ollama.ai
   - Baixe um modelo (ex: `ollama pull llama3`)
   - O sistema usa `http://localhost:11434` por padrão

## 🚀 Como Usar

### Iniciar o Dashboard

```bash
streamlit run dashboard.py
```

O dashboard será aberto automaticamente no navegador (geralmente em `http://localhost:8501`).

### Configuração Inicial

1. **Conectar Google APIs**:
   - Clique em "🔌 Conectar Google APIs" na barra lateral
   - Autorize o acesso quando solicitado

2. **Carregar Dados da Planilha**:
   - Informe o ID da planilha Google Sheets (encontrado na URL) ou cole a URL completa
   - Opcionalmente, informe o nome da aba (deixe vazio para primeira aba)
   - Clique em "📥 Carregar Dados"
   
   **Exemplo de ID**: `1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8`
   
   **Exemplo de URL completa**: `https://docs.google.com/spreadsheets/d/1IldiJwcZFkxNEpZ5nUj0ZodGkf3QgUhY1VcLzklDNs8/edit`

3. **Monitorar**:
   - O dashboard será atualizado automaticamente
   - Use o filtro de turma para visualizar Turma A ou B separadamente
   - Ative a atualização automática para monitoramento contínuo

## 📊 Estrutura da Planilha

A planilha Google Sheets deve conter colunas que serão automaticamente mapeadas para:

- **Turma**: Turma do cursista (A ou B) - pode estar em colunas como:
  - "Indique abaixo o melhor período para realização das ATIVIDADES SÍNCRONAS"
  - "Turma"
  - "Período"
  
- **Grupo**: Número do grupo temático (1 a 10) - coluna "Grupo"

- **Nome**: Nome completo do cursista - pode estar em colunas como:
  - "Nome completo (sem abreviação)"
  - "Nome completo"
  - "Nome"

- **Email**: Email do cursista - pode estar em colunas como:
  - "Escreva o e-mail (g-mail) o qual você irá acessar as Aulas Síncronas pelo Google Meet"
  - "E-mail"
  - "Email"
  - "G-mail"

- **Telefone**: Telefone/WhatsApp (opcional) - pode estar em colunas como:
  - "Número do telefone com DDD (WhatsApp)"
  - "Telefone"
  - "WhatsApp"

### Mapeamento Automático

O sistema detecta automaticamente as colunas usando padrões de busca. Não é necessário renomear as colunas da planilha - o sistema encontrará as colunas corretas baseado no conteúdo do cabeçalho.

### Exemplo de Planilha

| Indique abaixo o melhor período... | Grupo | Nome completo (sem abreviação) | Escreva o e-mail (g-mail)... | Número do telefone com DDD (WhatsApp) |
|-----------------------------------|-------|--------------------------------|----------------------------|--------------------------------------|
| Turma A | 1 | João Silva | joao.silva@email.com | (85) 99999-9999 |
| Turma A | 1 | Maria Santos | maria.santos@email.com | (85) 88888-8888 |
| Turma B | 2 | Pedro Oliveira | pedro.oliveira@email.com | (85) 77777-7777 |

## 🔧 Configuração

### Variáveis de Ambiente (Opcional)

Você pode configurar as seguintes variáveis de ambiente:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3"
export GOOGLE_SPREADSHEET_ID="seu-id-da-planilha"
```

### Arquivo config.py

As configurações principais estão em `config.py`:

- `OLLAMA_BASE_URL`: URL base do Ollama
- `OLLAMA_MODEL`: Modelo a ser usado
- `DASHBOARD_REFRESH_INTERVAL`: Intervalo de atualização automática (segundos)
- `NUM_GRUPOS`: Número de grupos temáticos (padrão: 10)
- `TURMAS`: Lista de turmas (padrão: ['A', 'B'])

## 📁 Estrutura do Projeto

```
meet/
├── dashboard.py              # Aplicação Streamlit principal
├── google_integration.py     # Integração com Google APIs
├── monitor.py                # Lógica de monitoramento
├── agente_ia.py              # Agente IA com Ollama
├── config.py                 # Configurações
├── requirements.txt          # Dependências
├── README.md                 # Este arquivo
├── quickstart.py             # Script de teste (existente)
├── token.json                # Token OAuth2 (gerado automaticamente)
└── credentials.json          # Credenciais OAuth2 (você precisa fornecer)
```

## 🔍 Funcionalidades do Dashboard

### Visão Geral
- Métricas totais: esperados, presentes, ausentes, em sala errada
- Percentuais de presença
- Timestamp da última atualização
- Filtro por turma (A, B ou Todas)

### Visualizações
- Gráfico de barras: Presença por grupo (filtrado por turma)
- Gráfico de pizza: Distribuição geral

### Status por Sala
- Cards visuais para cada combinação de turma e grupo
- Total de 20 salas: 10 grupos × 2 turmas (A e B)
- Indicadores de status (verde/amarelo/vermelho)
- Detalhes de participantes presentes, ausentes e em sala errada
- Filtro permite visualizar apenas uma turma por vez

### Lista de Problemas
- Tabela com todos os participantes com problemas
- Filtro por turma
- Download em CSV

### Recomendações da IA
- Análise automática de discrepâncias
- Problemas principais identificados
- Recomendações práticas
- Ações sugeridas em ordem de prioridade

## ⚠️ Limitações Conhecidas

1. **Google Meet API**: A API do Google Meet tem limitações para listar participantes de breakout rooms em tempo real. Atualmente, o sistema está preparado para essa funcionalidade, mas pode ser necessário usar outras abordagens (como relatórios administrativos do Google Workspace) em produção.

2. **Participantes Reais**: Por enquanto, a atualização de participantes reais precisa ser implementada ou simulada. Em produção, isso viria da Google Meet API ou de outra fonte de dados.

## 🐛 Solução de Problemas

### Erro de Autenticação / Scopes Insuficientes
- **Erro**: `Request had insufficient authentication scopes` ou `ACCESS_TOKEN_SCOPE_INSUFFICIENT`
- **Solução**: 
  1. Delete o arquivo `token.json`: `rm token.json` ou `./reset_auth.sh`
  2. Execute o dashboard novamente: `streamlit run dashboard.py`
  3. Clique em "Conectar Google APIs" e autorize TODOS os scopes solicitados
  4. Verifique se o arquivo `credentials.json` está no diretório
  5. Verifique se os scopes necessários estão habilitados no Google Cloud Console:
     - Google Meet API
     - Google Sheets API
     - Google Calendar API

### Erro: API não habilitada (accessNotConfigured)
- **Erro**: `Google Calendar API has not been used in project... or it is disabled`
- **Solução**:
  1. Acesse o [Google Cloud Console - APIs](https://console.cloud.google.com/apis/library)
  2. Selecione o projeto: **133165406108**
  3. Habilite as seguintes APIs:
     - [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
     - [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
     - [Google Meet API](https://console.cloud.google.com/apis/library/meet.googleapis.com)
  4. Aguarde alguns minutos para a propagação
  5. Tente novamente
  
  **Alternativa**: Use a opção "Link Manual" no dashboard para informar o link do meeting diretamente, sem precisar do Calendar API.

### Erro ao Carregar Planilha
- Verifique se o ID da planilha está correto
- Verifique se a planilha está compartilhada com a conta Google autenticada
- Verifique se as colunas necessárias existem na planilha

### Erro com Ollama
- Verifique se o Ollama está rodando: `ollama list`
- Verifique se o modelo está instalado: `ollama pull llama3`
- Verifique a URL em `config.py` ou variável de ambiente

## 📝 Notas

- O sistema foi projetado para trabalhar com breakout rooms dentro de um único Google Meet
- Os cursistas são divididos em duas turmas (A e B), cada uma com grupos temáticos de 1 a 10
- O agente de IA fornece análises e recomendações, mas não executa ações automáticas

## 🤝 Contribuindo

Para melhorias ou correções, por favor:
1. Verifique a estrutura da planilha
2. Teste com dados reais
3. Documente mudanças significativas

## 📄 Licença

Este projeto é para uso interno.

