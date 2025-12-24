---
description: Rotina semanal de comparação - antes dos encontros síncronos
---

# Rotina Semanal - Comparação Planilhas vs Avamec

**Quando executar:** Antes de cada encontro síncrono da turma (semanalmente)

**Objetivo:** Verificar divergências entre status das planilhas e Avamec, identificar cursistas com notas pendentes

---

## Passo 1: Atualizar Dados das Planilhas

```bash
cd /home/emanoel/proditec
python3 src/core/consolidate_grades.py
```

**Resultado:** Atualiza `data/grades_consolidados.csv` com dados mais recentes do Google Sheets

---

## Passo 2: Extrair Status do Avamec

// turbo
```bash
python3 scripts/scrape_avamec_completo.py
```

**O que faz:**
- Navega automaticamente por todos os grupos (Turma A e B)
- Clica em "Visão agrupada" em cada grupo
- Extrai situação parcial de todos os cursistas
- Ignora cursistas cancelados/desistentes
- Salva em `data/avamec_completo.json`

**Tempo estimado:** ~5-10 minutos (depende da conexão)

---

## Passo 3: Analisar Comparação no Dashboard

```bash
streamlit run src/compara_emails.py
```

**No navegador:**
1. Acesse http://localhost:8501
2. No menu lateral, selecione **"Comparação Planilhas vs Avamec"**
3. Use os filtros para selecionar a turma do próximo encontro
4. Analise:
   - **🔴 Divergências:** Cursistas com status diferente entre planilhas e Avamec
   - **⏳ Aguardando:** Cursistas com notas ainda não lançadas pelos ATTs
   - **Gráficos:** Distribuição de status e notas

---

## Passo 4: Gerar Relatório (Opcional)

// turbo
```bash
python3 scripts/comparacao_status.py > relatorios/comparacao_$(date +%Y%m%d).txt
```

**Resultado:** Relatório em texto com todas as divergências e estatísticas

---

## Passo 5: Comunicar Divergências

**Para os ATTs:**
- Informar cursistas com divergências de status
- Listar cursistas aguardando lançamento de notas

**Para a Coordenação:**
- Apresentar estatísticas gerais
- Destacar grupos com mais pendências
- Usar gráficos do dashboard em apresentações

---

## Passo 6: Criar Backup (Importante!)

// turbo
```bash
# Backup das planilhas consolidadas
cp data/grades_consolidados.csv data/backups/grades_$(date +%Y%m%d).csv

# Backup dos dados do Avamec
cp data/avamec_completo.json data/backups/avamec_$(date +%Y%m%d).json
```

**Importante:** Permite rastrear mudanças de status ao longo do tempo

---

## Checklist Semanal

- [ ] Atualizar dados das planilhas
- [ ] Extrair status do Avamec
- [ ] Analisar comparação no dashboard
- [ ] Identificar divergências
- [ ] Comunicar ATTs e coordenação
- [ ] Criar backups

---

## Dicas

- **Timing:** Execute 1-2 dias antes do encontro síncrono para dar tempo aos ATTs corrigirem divergências
- **Divergências comuns:** Notas lançadas no Avamec mas não atualizadas nas planilhas
- **Prioridade:** Focar em cursistas reprovados nas planilhas mas aprovados no Avamec (possível erro)
