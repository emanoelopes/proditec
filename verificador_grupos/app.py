import os
import re
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for

# --- Configuração do App ---

app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-forte' # Necessário para 'flash messages'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Regex para extrair e-mails de um bloco de texto
EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+'

# --- Funções de Lógica Principal ---

def load_expected_data(spreadsheet_path):
    """
    Carrega a planilha (Excel ou CSV) e a transforma em um dicionário.

    Assume que a planilha tem as colunas 'Email' e 'Grupo'.

    Args:
        spreadsheet_path (str): O caminho para o arquivo da planilha.

    Returns:
        dict: Um dicionário onde a chave é o e-mail (lowercase) 
              e o valor é o número do grupo (int).
              Ex: {'aluno1@gmail.com': 1, 'aluno2@gmail.com': 3}
    """
    try:
        if spreadsheet_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(spreadsheet_path)
        elif spreadsheet_path.endswith('.csv'):
            df = pd.read_csv(spreadsheet_path)
        else:
            raise ValueError("Formato de arquivo não suportado.")

        # Normaliza nomes das colunas (ex: ' Email ', 'Grupo')
        df.columns = df.columns.str.strip().str.lower()

        # Encontra as colunas corretas (procura por 'email' e 'grupo')
        email_col = next(col for col in df.columns if 'email' in col)
        group_col = next(col for col in df.columns if 'grupo' in col)

        # Transforma em dicionário, limpando e-mails e convertendo grupo para int
        expected_data = {}
        for _, row in df.iterrows():
            email = str(row[email_col]).strip().lower()
            if '@' in email: # Garante que é um e-mail válido
                expected_data[email] = int(row[group_col])
        
        return expected_data

    except Exception as e:
        print(f"Erro ao ler planilha: {e}")
        return None

def parse_actual_data(form_data):
    """
    Extrai e-mails dos 10 campos de <textarea> do formulário.

    Args:
        form_data (ImmutableMultiDict): O request.form do Flask.

    Returns:
        dict: Um dicionário onde a chave é o número do grupo (int)
              e o valor é um set de e-mails (lowercase) encontrados.
              Ex: {1: {'aluno1@gmail.com', 'aluno4@gmail.com'}, 2: set()}
    """
    actual_data_by_group = {}
    for i in range(1, 11):
        group_key = f'group{i}'
        pasted_text = form_data.get(group_key, '')
        
        # Encontra todos os e-mails no texto colado e os normaliza
        emails_found = re.findall(EMAIL_REGEX, pasted_text)
        emails_set = {email.strip().lower() for email in emails_found}
        
        actual_data_by_group[i] = emails_set
    
    return actual_data_by_group

def generate_discrepancy_report(expected_data, actual_data_by_group):
    """
    Compara os dados esperados (planilha) com os dados reais (formulário)
    e gera um relatório de divergências.

    Args:
        expected_data (dict): {email: grupo_esperado}
        actual_data_by_group (dict): {grupo_real: {email1, email2}}

    Returns:
        list: Uma lista de strings, onde cada string é uma divergência.
    """
    discrepancies = []
    5
    # Inverte o 'actual_data' para fácil consulta: {email: grupo_real}
    actual_email_location = {}
    all_actual_emails = set()
    
    for group_num, emails_set in actual_data_by_group.items():
        for email in emails_set:
            if email in actual_email_location:
                # E-mail encontrado em múltiplos grupos!
                discrepancies.append(
                    f"ERRO MÚLTIPLO: '{email}' foi encontrado no Grupo {group_num} e também no Grupo {actual_email_location[email]}."
                )
            actual_email_location[email] = group_num
            all_actual_emails.add(email)

    all_expected_emails = set(expected_data.keys())

    # --- Verificação 1: Alunos na planilha que estão no grupo errado ---
    for email in (all_expected_emails & all_actual_emails):
        expected_group = expected_data[email]
        actual_group = actual_email_location[email]
        
        if expected_group != actual_group:
            discrepancies.append(
                f"ALOCAÇÃO INCORRETA: '{email}' deveria estar no Grupo {expected_group}, mas foi encontrado no Grupo {actual_group}."
            )

    # --- Verificação 2: Alunos na planilha que não estão em NENHUM grupo ---
    missing_from_all_groups = all_expected_emails - all_actual_emails
    for email in missing_from_all_groups:
        expected_group = expected_data[email]
        discrepancies.append(
            f"AUSENTE: '{email}' (esperado no Grupo {expected_group}) não foi encontrado em NENHUM grupo."
        )

    # --- Verificação 3: Alunos nos grupos que não estão na planilha ---
    extra_in_groups = all_actual_emails - all_expected_emails
    for email in extra_in_groups:
        actual_group = actual_email_location[email]
        discrepancies.append(
            f"NÃO ESTÁ NA PLANILHA: '{email}' (encontrado no Grupo {actual_group}) não consta na planilha mestre."
        )

    return discrepancies


# --- Rotas da Aplicação Web ---

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário de upload."""
    return render_template('index.html')

@app.route('/verificar', methods=['POST'])
def verificar_grupos():
    """
    Recebe os arquivos, processa os dados e mostra o relatório.
    """
    if 'spreadsheet' not in request.files:
        flash('Nenhum arquivo de planilha enviado.')
        return redirect(url_for('index'))

    file = request.files['spreadsheet']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect(url_for('index'))

    if file:
        # Salva a planilha temporariamente
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # 1. Carrega dados esperados (Planilha)
        expected_data = load_expected_data(filepath)
        if expected_data is None:
            flash('Erro ao ler a planilha. Verifique se as colunas "Email" e "Grupo" existem.')
            return redirect(url_for('index'))

        # 2. Carrega dados reais (Formulário)
        actual_data = parse_actual_data(request.form)
        
        # 3. Gera o relatório
        report = generate_discrepancy_report(expected_data, actual_data)

        # 4. Limpa o arquivo salvo (opcional, mas bom)
        os.remove(filepath)
        
        # 5. Renderiza a página de relatório
        return render_template('report.html', report=report, total=len(report))

    return redirect(url_for('index'))

# --- Página de Relatório ---
# (Poderia ser um arquivo separado, mas para simplificar...)

@app.template_filter()
def report_html(report_items):
    """Um filtro para formatar o relatório em HTML (usado no report.html)"""
    if not report_items:
        return "<p style='color: green; font-size: 1.2em;'>🎉 Nenhuma divergência encontrada! Todos os grupos estão corretos.</p>"
    
    html = "<ul>"
    for item in report_items:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html

# Criamos um template simples para o relatório
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Divergências</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        li { margin-bottom: 10px; font-size: 1.1em; }
        li:contains('INCORRETA') { color: #D9534F; }
        li:contains('AUSENTE') { color: #F0AD4E; }
        li:contains('NÃO ESTÁ') { color: #5BC0DE; }
        li:contains('MÚLTIPLO') { color: #D9534F; font-weight: bold; }
        a { margin-top: 2em; display: inline-block; }
    </style>
</head>
<body>
    <h1>Relatório de Divergências</h1>
    <p>Total de divergências encontradas: <strong>{{ total }}</strong></p>
    <hr>
    
    {% if total > 0 %}
        <ul>
        {% for item in report %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p style='color: green; font-size: 1.2em;'>🎉 Nenhuma divergência encontrada! Todos os grupos estão corretos.</p>
    {% endif %}

    <a href="/">Voltar e verificar novamente</a>
</body>
</html>
"""

# Adicionamos o template 'report.html' diretamente no código para simplificar
# Em um projeto real, você criaria 'templates/report.html'
app.jinja_loader.searchpath = ['templates'] # Define o path
app.jinja_loader.load = lambda env, name, globals: \
    env.from_string(REPORT_TEMPLATE) if name == 'report.html' else \
    app.jinja_loader.load(env, name, globals)


# --- Executar o App ---
if __name__ == '__main__':
    app.run(debug=True) # debug=True ajuda no desenvolvimento