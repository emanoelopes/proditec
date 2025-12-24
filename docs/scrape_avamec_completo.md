# Scraper Automático do Avamec

Script para extrair automaticamente a "Situação Parcial" de todos os alunos de todas as turmas e grupos.

## Como usar:

```bash
python3 scripts/scrape_avamec_completo.py
```

## O que o script faz automaticamente:

1. **Login**: Carrega cookies salvos ou solicita login manual uma vez
2. **Navega pelas turmas**:
   - Turma A: `https://avamecinterativo.mec.gov.br/app/dashboard/environments/179/gradebook`
   - Turma B: `https://avamecinterativo.mec.gov.br/app/dashboard/environments/180/gradebook`
3. **Para cada grupo (01-10)**:
   - Clica no seletor do grupo
   - Clica em "Visão agrupada"
   - Lê toda a tabela de notas
   - Extrai nome do aluno e situação parcial
4. **Salva tudo** em `data/avamec_completo.json`

## Saída:

```json
{
  "data_extracao": "2025-12-24T16:40:00",
  "total_turmas": 2,
  "total_grupos": 20,
  "total_alunos": 489,
  "alunos": [
    {
      "nome": "Nome do Aluno",
      "turma": "Turma A",
      "grupo": "Turma A - Grupo 01",
      "situacao_parcial": "9.5",
      "data_extracao": "2025-12-24T16:40:15"
    }
  ]
}
```

## Depois de extrair:

```bash
# Atualizar tabela comparativa com TODOS os dados
python3 scripts/comparacao_status.py
```

## Nota:

O script tenta automatizar a navegação, mas pode precisar de ajustes nos seletores CSS dependendo da estrutura exata do HTML do Avamec. Se a navegação automática falhar, o script solicitará intervenção manual.
