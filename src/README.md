# 📧 Comparador de Emails - Google Meet

Sistema para comparar emails de participantes do Google Meet com listas de convidados, identificando participantes não convidados e direcionando-os aos grupos temáticos corretos.

## 🚀 Funcionalidades

- **Upload de Planilhas**: Suporte para CSV, Excel e arquivos de texto
- **Extração Automática**: Extrai emails e nomes de atas do Google Meet
- **Comparação Inteligente**: Identifica participantes não convidados
- **Visualizações**: Gráficos de distribuição e recorrência de domínios
- **Exportação**: Download dos resultados em CSV
- **Interface Amigável**: Aplicação web com Streamlit

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

1. **Clone ou baixe os arquivos**:
   ```bash
   # Navegue até o diretório
   cd /caminho/para/avamec/src
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Como Usar

### Método 1: Script Automático
```bash
python run_app.py
```

### Método 2: Streamlit Direto
```bash
streamlit run compara_emails.py
```

### Método 3: Com Parâmetros Personalizados
```bash
streamlit run compara_emails.py --server.port 8502 --server.address 0.0.0.0
```

## 📊 Formatos de Arquivo Suportados

### 1. Ata de Participantes (Google Meet)
- **CSV**: Colunas `nome` e `email`
- **Excel**: Colunas `nome` e `email`
- **TXT**: Texto bruto da ata (extração automática)

### 2. Lista de Convidados
- **CSV**: Coluna `email` (obrigatória)
- **Excel**: Coluna `email` (obrigatória)

### 3. Grupos Temáticos (Opcional)
- **CSV**: Colunas `email` e `grupo_tematico`
- **Excel**: Colunas `email` e `grupo_tematico`

## 🔧 Estrutura dos Dados

### Ata de Participantes (Exemplo CSV)
```csv
nome,email
João Silva,joao.silva@email.com
Maria Santos,maria.santos@email.com
```

### Lista de Convidados (Exemplo CSV)
```csv
email
joao.silva@email.com
maria.santos@email.com
pedro.oliveira@email.com
```

### Grupos Temáticos (Exemplo CSV)
```csv
email,grupo_tematico
joao.silva@email.com,Grupo A
maria.santos@email.com,Grupo B
```

## 📈 Recursos da Interface

### Métricas Principais
- Total de participantes
- Número de convidados
- Número de não convidados
- Percentual de não convidados

### Visualizações
- **Gráfico de Pizza**: Distribuição de participantes
- **Gráfico de Barras**: Top 10 domínios de email (não convidados)
- **Tabela Interativa**: Lista de participantes não convidados

### Funcionalidades
- **Upload Múltiplo**: Carregue diferentes tipos de arquivo
- **Visualização de Dados**: Preview dos dados carregados
- **Download**: Exporte resultados em CSV
- **Responsivo**: Interface adaptável

## 🎨 Personalização

### Modificar Colunas
Se suas planilhas usam nomes de colunas diferentes, você pode modificar os parâmetros:

```python
# Para participantes
comparador.extrair_emails_participantes(
    coluna_email='seu_email', 
    coluna_nome='seu_nome'
)

# Para convidados
comparador.comparar_participantes_convidados(
    coluna_email_convidados='seu_email_convidados'
)
```

## 🐛 Solução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de Porta em Uso
```bash
streamlit run compara_emails.py --server.port 8502
```

### Problemas com Encoding
- Salve arquivos CSV com encoding UTF-8
- Para Excel, use formato .xlsx

## 📝 Exemplo de Uso Completo

1. **Prepare os arquivos**:
   - Ata do Google Meet (CSV/TXT)
   - Lista de convidados (CSV/Excel)
   - Grupos temáticos (opcional)

2. **Execute a aplicação**:
   ```bash
   python run_app.py
   ```

3. **Na interface web**:
   - Faça upload dos arquivos na barra lateral
   - Clique em "Executar Comparação"
   - Visualize os resultados
   - Baixe o relatório em CSV

## 🔒 Segurança

- Os dados são processados localmente
- Nenhuma informação é enviada para servidores externos
- Arquivos temporários são limpos automaticamente

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se os arquivos estão no formato correto
3. Verifique se as colunas têm os nomes esperados

## 🚀 Próximas Versões

- [ ] Suporte a mais formatos de arquivo
- [ ] Análise de padrões de participação
- [ ] Integração com APIs do Google Meet
- [ ] Relatórios em PDF
- [ ] Dashboard de métricas históricas


