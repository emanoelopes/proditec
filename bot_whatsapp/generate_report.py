import pandas as pd
import glob
import sys
import re

# Template da mensagem
# Pode ser ajustado conforme necessário
MESSAGE_TEMPLATE = """Prezado(a) {nome_articulador},

Informamos o status dos envios de mensagens via WhatsApp para os cursistas de {municipio}.

Quantidade de cursistas que já receberam a mensagem: {qtd_entregue}

Atenciosamente,
Coordenação"""

def normalize_phone(phone):
    s = str(phone).strip().replace('.0', '')
    # Remove chars
    s = re.sub(r'\D', '', s)
    # Remove 55 prefix if likely country code
    if s.startswith('55') and len(s) > 11:
        s = s[2:]
    return s

def load_delivered_phones():
    files = glob.glob("delivered_report_*.csv")
    print(f"Lendo relatórios de entrega: {files}")
    
    all_phones = set()
    for f in files:
        try:
            df = pd.read_csv(f)
            if 'phone' in df.columns:
                for p in df['phone'].dropna():
                    norm = normalize_phone(p)
                    if norm:
                        all_phones.add(norm)
        except Exception as e:
            print(f"Erro ao ler {f}: {e}")
    return all_phones

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_report.py <caminho_csv_cursistas>")
        print("Exemplo: python3 generate_report.py cursistas.csv")
        # Fallback check
        if os.path.exists("cursistas.csv"):
            csv_path = "cursistas.csv"
            print("Encontrado 'cursistas.csv', usando-o.")
        else:
            return
    else:
        csv_path = sys.argv[1]

    # 1. Carregar Articuladores
    # Assumindo CSV sem cabeçalho: Municipio, UF, Nome, Email, Phone...
    try:
        art_df = pd.read_csv('articuladores_2026_1.csv', header=None)
        # Ajuste conforme estrutura real verificada com 'cat'
        # Col 0: Municipio, Col 2: Nome, Col 3: Email
        art_df = art_df.rename(columns={0: 'Municipio', 2: 'Nome', 3: 'Email'})
        print(f"Carregados {len(art_df)} articuladores.")
    except Exception as e:
        print(f"Erro ao ler articuladores_2026_1.csv: {e}")
        return

    # 2. Carregar Telefones Entregues
    sent_phones = load_delivered_phones()
    print(f"Total de telefones únicos que receberam mensagem: {len(sent_phones)}")

    # 3. Carregar Cursistas
    try:
        cursistas_df = pd.read_csv(csv_path)
        print(f"Carregados {len(cursistas_df)} registros de cursistas.")
    except Exception as e:
        print(f"Erro ao ler {csv_path}: {e}")
        return

    # Identificar colunas chaves
    cols = cursistas_df.columns
    secretaria_col = next((c for c in cols if 'secretaria' in c.lower()), None)
    phone_col = next((c for c in cols if 'tel' in c.lower() or 'cel' in c.lower() or 'phone' in c.lower() or 'whatsapp' in c.lower()), None)

    if not secretaria_col or not phone_col:
        print(f"Colunas não encontradas no CSV de cursistas. Disponíveis: {list(cols)}")
        return

    print(f"Usando colunas: Secretaria='{secretaria_col}', Telefone='{phone_col}'")

    # 4. Gerar Relatório
    report_data = []

    for idx, art in art_df.iterrows():
        municipio_art = str(art['Municipio']).strip()
        nome_art = str(art['Nome']).strip()
        email_art = str(art['Email']).strip()
        
        # Filtrar cursistas deste municipio
        # Normalização simples (strip + ignore case se necessário)
        # Aqui fazemos match exato (com strip)
        mask = cursistas_df[secretaria_col].astype(str).str.strip() == municipio_art
        meus_cursistas = cursistas_df[mask]
        
        if meus_cursistas.empty:
            # Tentar caixa alta
            mask = cursistas_df[secretaria_col].astype(str).str.strip().str.upper() == municipio_art.upper()
            meus_cursistas = cursistas_df[mask]

        total_lista = len(meus_cursistas)
        entregues = 0
        
        for _, c_row in meus_cursistas.iterrows():
            p = normalize_phone(c_row[phone_col])
            if p in sent_phones:
                entregues += 1
        
        # Montar Mensagem
        msg = MESSAGE_TEMPLATE.format(
            nome_articulador=nome_art,
            municipio=municipio_art,
            qtd_entregue=entregues
        )
        
        report_data.append({
            'Municipio': municipio_art,
            'Articulador_Nome': nome_art,
            'Articulador_Email': email_art,
            'Total_Cursistas': total_lista,
            'Receberam_Mensagem': entregues,
            'Mensagem_Email': msg
        })

    # Salvar
    report_df = pd.DataFrame(report_data)
    report_df.to_csv('relatorio_final_coordenacao.csv', index=False)
    print("\nRelatório gerado com sucesso: 'relatorio_final_coordenacao.csv'")
    
    # Preview
    print("\nExemplo das primeiras linhas:")
    print(report_df[['Municipio', 'Receberam_Mensagem']].head())

if __name__ == "__main__":
    import os
    main()
