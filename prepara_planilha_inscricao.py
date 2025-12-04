# This script reads an Excel file, processes the data by renaming columns,
# separates the data into groups, and saves each group into a new Excel
# file based on a template. Finally, it compresses the generated files.

import pandas as pd
import os

# Load the main Excel file with error handling
try:
    df = pd.read_excel("/home/emanoel/Dropbox/avamec/inscricoes/Cadastro avamec Quarta Lista 080825.xlsx")
except FileNotFoundError:
    print("Arquivo principal não encontrado. Verifique o caminho e tente novamente.")
    exit(1)

# Define the renaming mapping
rename_mapping = {
    'Nome completo ': 'nome',
    'E-mail (g-mail) -  Aulas Síncronas pelo Google Meet. ': 'email',
    'Escreva o número do seu Cadastro de Pessoa Física (CPF). *': 'CPF',
    'Data de Nascimento:\nFormato (dia, mês, ano)\n*': 'data_nascimento',
    'Turma A ou B': 'turma',
    'Pequeno Grupo': 'grupo'
}
df = df.rename(columns=rename_mapping)

# Group the data by 'grupo'
grouped_by_grupo = df.groupby('grupo')

# Load the template Excel file with error handling
template_path = "/home/emanoel/Dropbox/avamec/inscricoes/planilha-modelo-de-importacao-de-membros.xlsx"
try:
    template_df = pd.read_excel(template_path)
except FileNotFoundError:
    print("Arquivo de template não encontrado. Verifique o caminho e tente novamente.")
    exit(1)

template_df = template_df.iloc[0:0]

# Define the column mapping from the original data to the template
column_mapping = {
    'nome': '[1] Nome do usuário',
    'email': '[2] E-mail',
    'CPF': '[3]CPF',
    'data_nascimento': '[4] Data de nascimento (opcional)'
}

# Define the value for the 'Função' column
role_value = 'Aluno'

# Create a directory for the filled templates
filled_output_dir = "/home/emanoel/Dropbox/avamec/pequenos_grupos_templates_preenchidos"
os.makedirs(filled_output_dir, exist_ok=True)

# Format the 'data_nascimento' column
df['data_nascimento'] = pd.to_datetime(df['data_nascimento']).dt.strftime('%d/%m/%Y')

# Iterate through each group, fill the template, and save the new file
for group_key, group_df in grouped_by_grupo:
    filled_template_df = pd.DataFrame(columns=template_df.columns)
    for original_col, template_col in column_mapping.items():
        filled_template_df[template_col] = group_df[original_col].values
    filled_template_df['[5] Função (Administrador, Professor, Tutor ou Aluno)'] = role_value

    output_file_name = f"template_pequeno_grupo_{group_key}_preenchido.xlsx"
    output_path = os.path.join(filled_output_dir, output_file_name)
    filled_template_df.to_excel(output_path, index=False)
    print(f"Filled template for group {group_key} saved to {output_path}")

# Compress the generated files into a zip archive
!zip -r /content/pequenos_grupos_templates_preenchidos.zip /content/pequenos_grupos_templates_preenchidos/

print("\nAll tasks completed. The filled templates have been saved and compressed.")