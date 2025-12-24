# Scraper de Situação Parcial - Avamec

Este script extrai a "Situação parcial" de todos os alunos diretamente do Avamec (visão agrupada).

## Como usar:

### 1. Primeira execução (com login manual):
```bash
python3 scripts/scrape_avamec_status.py
```

O navegador abrirá. Faça login e pressione ENTER. Os cookies serão salvos.

### 2. Execuções seguintes (automático):
```bash
python3 scripts/scrape_avamec_status.py
```

### 3. Comparar status entre dois períodos:
```bash
# Criar backup do status atual
cp data/avamec_status_situacao.json data/backups/avamec_status_$(date +%Y%m%d).json

# Depois de alguns dias, rodar novamente e comparar
python3 scripts/compare_avamec_status.py
```

## ⚠️ IMPORTANTE:

Os **seletores CSS** no script são GENÉRICOS e precisam ser ajustados para o HTML real do Avamec.

Para ajustar:
1. Acesse o Avamec manualmente
2. Abra o DevTools (F12)
3. Inspecione a tabela de notas
4. Identifique os seletores CSS corretos
5. Atualize no arquivo `scripts/scrape_avamec_status.py`

## Arquivos gerados:

- `data/avamec_cookies.json` - Cookies de login
- `data/avamec_status_situacao.json` - Status extraído
- `data/backups/avamec_status_YYYYMMDD.json` - Backups diários
