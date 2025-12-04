# Define file paths (update these paths if your files are located elsewhere)
cursistas_file = '/home/emanoel/Dropbox/avamec/inscricoes/Cursistas Turma A/Cursistas Turma_A.xlsx'

# Define matching columns
matching_column_cursistas = '[0] login'
matching_column_ava = 'Login do Membro'
error_column_ava = 'Erro Apresentado?'
login_existente_column = 'Login existente'

# Load the cursistas dataframe once
try:
    df_cursistas = pd.read_excel(cursistas_file)
    # Clean the matching column in df_cursistas once
    df_cursistas[matching_column_cursistas] = df_cursistas[matching_column_cursistas].astype(str).str.strip().str.lower()
except FileNotFoundError as e:
    print(f"Error loading cursistas file: {e}. Make sure the file path is correct.")
    # Use finish_task here as the cursistas file is essential for the entire process
    # If this file is not found, we cannot proceed with any AVA report file.
    # Assuming 'df_cursistas' is required for all subsequent steps.
    # If it were possible to continue without it, we would use 'continue'.
    # However, given the merge operation, df_cursistas is necessary.
    # Therefore, we signal a failure for the entire subtask.
    raise SystemExit(f"Error loading cursistas file: {e}. Cannot proceed.")

def verificar_emails(cursistas_file, emails_file):
    """
    Verifica se os emails fornecidos existem na planilha de cursistas.
    
    Args:
        cursistas_file (str): Caminho para o arquivo de cursistas
        emails_file (str): Caminho para o arquivo com lista de emails
    """
    try:
        # Carrega planilha de cursistas
        df_cursistas = pd.read_excel(cursistas_file)
        
        # Carrega arquivo com emails para verificar
        with open(emails_file, 'r') as f:
            emails_verificar = [email.strip().lower() for email in f.readlines()]
        
        # Converte emails dos cursistas para lowercase para comparação
        emails_cursistas = df_cursistas['[2] E-mail'].str.strip().str.lower()
        
        # Verifica emails
        emails_encontrados = []
        emails_nao_encontrados = []
        
        for email in emails_verificar:
            if email in emails_cursistas.values:
                emails_encontrados.append(email)
            else:
                emails_nao_encontrados.append(email)
        
        # Exibe resultados
        print("\nResultados da verificação de emails:")
        print(f"Total de emails verificados: {len(emails_verificar)}")
        print(f"Emails encontrados: {len(emails_encontrados)}")
        print(f"Emails não encontrados: {len(emails_nao_encontrados)}")
        
        if emails_nao_encontrados:
            print("\nEmails não encontrados na planilha:")
            for email in emails_nao_encontrados:
                print(f"- {email}")
                
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# ...existing code...
# Loop through the identified AVA report files
for ava_report_file in ava_report_files:
    print(f"\nProcessing file: {ava_report_file}")
    try:
        # Load the current AVA report dataframe
        df_ava = pd.read_csv(ava_report_file)

        # Clean the matching column in df_ava
        df_ava[matching_column_ava] = df_ava[matching_column_ava].astype(str).str.strip().str.lower()

        # Filter rows where 'Erro Apresentado?' is 'Sim'
        # Add error handling for missing 'Erro Apresentado?' column
        if error_column_ava not in df_ava.columns:
            print(f"Error processing {ava_report_file}: Missing required column '{error_column_ava}'. Skipping this file.")
            continue
        errored_cursistas_df = df_ava[df_ava[error_column_ava] == 'Sim'].copy()

        # Merge with the entire df_cursistas dataframe using the cleaned login columns
        # Add error handling for missing matching columns during merge
        if matching_column_ava not in errored_cursistas_df.columns or matching_column_cursistas not in df_cursistas.columns:
             print(f"Error processing {ava_report_file}: Missing matching columns for merge ('{matching_column_ava}' or '{matching_column_cursistas}'). Skipping this file.")
             continue

        errored_cursistas_with_cursistas_info = pd.merge(
            errored_cursistas_df,
            df_cursistas,
            how='left',
            left_on=matching_column_ava,
            right_on=matching_column_cursistas
        )

        # Replace the values in the '[0] login' column with values from 'Login existente' where available
        # Add error handling for missing 'Login existente' column
        if login_existente_column in errored_cursistas_with_cursistas_info.columns:
             errored_cursistas_with_cursistas_info[matching_column_cursistas] = errored_cursistas_with_cursistas_info[login_existente_column].fillna(errored_cursistas_with_cursistas_info[matching_column_cursistas])
        else:
             print(f"Warning processing {ava_report_file}: Missing column '{login_existente_column}'. Cannot replace login values.")


        # Select only the columns that are present in df_cursistas and maintain their original order
        # Add error handling for selecting columns
        try:
            final_errored_cursistas_df = errored_cursistas_with_cursistas_info[df_cursistas.columns]
        except KeyError as e:
            print(f"Error processing {ava_report_file}: Error selecting columns - {e}. Skipping this file.")
            continue


        # Generate the output filename based on the current AVA report file name
        base_name = os.path.splitext(os.path.basename(ava_report_file))[0]
        output_excel_file = f'{base_name}_cursistas_com_erro.xlsx'

        # Save the result to a new Excel file
        final_errored_cursistas_df.to_excel(output_excel_file, index=False)
        print(f"Generated output file: '{output_excel_file}'")

    except FileNotFoundError as e:
        print(f"Error loading AVA report file: {e}. Skipping this file.")
        continue
    except KeyError as e:
        print(f"Error processing {ava_report_file}: Missing expected column - {e}. Skipping this file.")
        continue
    except ValueError as e:
        print(f"Error processing {ava_report_file}: Value error during processing - {e}. Skipping this file.")
        continue
    except Exception as e:
        print(f"An unexpected error occurred while processing {ava_report_file}: {e}. Skipping this file.")
        continue


print("\nProcessing complete.")

# Exemplo de chamada da função
verificar_emails('/home/emanoel/Downloads/avamec_inscricoes/Cursistas Turma A/Cursistas Turma_A.xlsx', '/home/emanoel/Downloads/avamec_inscricoes/Cursistas Turma A/emails_verificar.txt')