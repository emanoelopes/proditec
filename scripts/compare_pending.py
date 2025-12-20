import pandas as pd
import re
import sys

def normalize_phone(phone):
    s = str(phone).strip()
    s = re.sub(r'\D', '', s)
    if s.startswith('55') and len(s) > 11:
        s = s[2:]
    return s

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compare_pending.py <path_to_planilha4.csv>")
        return

    csv_path = sys.argv[1]
    
    # Load sent phones
    try:
        with open('sent_phones_list.txt', 'r') as f:
            sent_phones = set(line.strip() for line in f)
    except FileNotFoundError:
        print("sent_phones_list.txt not found. Run consolidate_logs.py first.")
        return

    print(f"Loaded {len(sent_phones)} sent phones.")

    # Load Planilha4
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return

    # Identify columns
    cols = df.columns
    # Find Secretaria
    secretaria_col = next((c for c in cols if 'secretaria' in c.lower()), None)
    # Find Phone
    phone_col = next((c for c in cols if 'tel' in c.lower() or 'cel' in c.lower() or 'phone' in c.lower() or 'whatsapp' in c.lower()), None)
    # Find Name
    name_col = next((c for c in cols if 'nome' in c.lower() or 'cursista' in c.lower()), None)

    if not secretaria_col:
        print("Column 'Secretaria' not found in CSV.")
        print(f"Available columns: {list(cols)}")
        return
    if not phone_col:
        print("Phone column not found (looked for 'tel', 'cel', 'phone', 'whatsapp').")
        print(f"Available columns: {list(cols)}")
        return

    print(f"Using columns: Secretaria='{secretaria_col}', Phone='{phone_col}', Name='{name_col}'")

    # Filter
    pending_list = []
    
    for idx, row in df.iterrows():
        phone_raw = row[phone_col]
        norm_phone = normalize_phone(phone_raw)
        
        if not norm_phone: # skip empty
            continue
            
        if norm_phone not in sent_phones:
            pending_list.append({
                'Secretaria': row[secretaria_col],
                'Nome': row[name_col] if name_col else 'N/A',
                'Telefone': norm_phone
            })

    # Group by Secretaria
    df_pending = pd.DataFrame(pending_list)
    
    if df_pending.empty:
        print("All contacts in the sheet have already received messages!")
    else:
        # Save to file
        df_pending.to_csv('pendentes_por_localidade.csv', index=False)
        print(f"Found {len(df_pending)} pending contacts.")
        print("Saved detailed list to 'pendentes_por_localidade.csv'.")
        
        # Print Summary
        summary = df_pending.groupby('Secretaria').size().reset_index(name='Count')
        print("\n--- Summary by Localidade ---")
        print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
