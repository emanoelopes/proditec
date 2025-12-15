import pandas as pd
import glob
import os

def load_delivered_phones():
    # Find all delivered_report files
    files = glob.glob("delivered_report_*.csv")
    print(f"Found {len(files)} delivered report files: {files}")
    
    all_phones = set()
    for f in files:
        try:
            # Try reading with header
            df = pd.read_csv(f)
            # Check if 'phone' column exists
            if 'phone' in df.columns:
                # Normalize phones: remove non-digits, remove 55 prefix if len > 11
                for p in df['phone'].dropna():
                    s = str(p).strip().replace('.0', '')
                    s = ''.join(filter(str.isdigit, s))
                    if s.startswith('55') and len(s) > 11:
                        s = s[2:]
                    all_phones.add(s)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    return all_phones

if __name__ == "__main__":
    phones = load_delivered_phones()
    print(f"Total unique delivered phones: {len(phones)}")
