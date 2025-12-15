import pandas as pd
import glob
import re
import os

def normalize_phone(phone):
    s = str(phone).strip()
    # Remove non-digits
    s = re.sub(r'\D', '', s)
    # If starts with 55 (Brazil) and length > 11, strip it
    if s.startswith('55') and len(s) > 11:
        s = s[2:]
    return s

# Define patterns
files_patterns = [
    'bot_whatsapp/delivered_report_20251212_*.csv',
    'bot_whatsapp/delivered_report_20251214_*.csv',
    'bot_whatsapp/relatorio_hoje_2025-12-12.csv'
]

sent_phones = set()
processed_files = 0

print("Reading log files...")
for pattern in files_patterns:
    for f in glob.glob(pattern):
        try:
            if os.path.getsize(f) == 0:
                continue
            df = pd.read_csv(f)
            if 'phone' in df.columns:
                phones = df['phone'].apply(normalize_phone).tolist()
                sent_phones.update(phones)
                processed_files += 1
                print(f"Propcessed {f}, found {len(phones)} records.")
        except Exception as e:
            print(f"Error reading {f}: {e}")

print(f"\nTotal unique sent phones: {len(sent_phones)}")

# Save to file
with open('sent_phones_list.txt', 'w') as f:
    for p in sent_phones:
        f.write(p + '\n')
print("Saved consolidated list to sent_phones_list.txt")
