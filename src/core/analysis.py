import pandas as pd
import numpy as np
import os
import re

def clean_column_name(col):
    col = str(col).strip()
    if 'cidade' in col.lower() and 'secretaria' in col.lower():
        return 'Cidade'
    if 'estado' in col.lower() and 'secretaria' in col.lower():
        return 'Estado'
    if 'média final' in col.lower():
        return 'Media_Final'
    if 'status' in col.lower() and 'nota' in col.lower():
        return 'Status_Nota'
    if 'status' in col.lower() and 'frequência' in col.lower():
        return 'Status_Frequencia'
    if 'diretor' in col.lower() and 'secretaria' in col.lower():
        return 'Cargo'
    if 'sexo' in col.lower():
        return 'Sexo'
    if 'nascimento' in col.lower():
        return 'Nascimento'
    if 'nome completo' in col.lower():
        return 'Nome'
    return col

def run_eda():
    base_path = '/home/emanoel/proditec'
    input_file = os.path.join(base_path, 'grades_consolidados.csv')
    output_file = os.path.join(base_path, 'processed_data.csv')
    
    # Read CSV skipping the first row (superheader)
    # The real header is on row 1 (0-indexed)
    print("Reading data...")
    try:
        df = pd.read_csv(input_file, header=1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Clean Column Names
    new_cols = []
    for col in df.columns:
        new_cols.append(clean_column_name(col))
    df.columns = new_cols
    
    print("Columns identified:", df.columns.tolist())
    
    # Filter for required columns
    required_cols = ['Nome', 'Cidade', 'Estado', 'Cargo', 'Sexo', 'Nascimento', 'Media_Final', 'Status_Nota', 'Status_Frequencia']
    
    # Check if all required columns exists (fuzzy match handled in clean_column_name)
    # Some might be missing or named differently if the regex didn't catch them
    # Let's inspect what we got
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Warning: Missing columns: {missing}")
    
    # Convert Media_Final to numeric
    # It might contain comma as decimal separator
    if 'Media_Final' in df.columns:
        df['Media_Final'] = df['Media_Final'].astype(str).str.replace(',', '.').replace('#DIV/0!', np.nan)
        df['Media_Final'] = pd.to_numeric(df['Media_Final'], errors='coerce')
        
    # Analysis 1: Performance by Municipality (Average Grade)
    if 'Cidade' in df.columns and 'Media_Final' in df.columns:
        city_perf = df.groupby('Cidade')['Media_Final'].mean().sort_values(ascending=False)
        print("\nTop 5 Cities by Performance:")
        print(city_perf.head())
        
        # Save aggregated for Dashboard? Or just save the clean DF
        
    # Feature: Extract Source Group from URL if available in the original raw read?
    # Actually, we consolidated it but when reading with header=1 we might have lost the "Source_Sheet_Title" column 
    # because it was added to the data rows corresponding to header=0.
    # Wait, consolidate_grades added 'Source_Sheet_Title' to the dataframe. 
    # Since we re-read the CSV skipping row 0, the column 'Source_Sheet_Title' should technically still be there 
    # IF it was in the header row 0. 
    # But in consolidate_grades, we added it to the dataframe. The CSV has it. 
    # Row 0 has "Source_Sheet_Title". Row 1 has "Source_Sheet_Title" (value) or empty?
    # Inspecting head output: The last columns were "Source_Sheet_Title", "Source_URL".
    # Since we skipped row 0, the header we are using is row 1. 
    # Row 1 might NOT have "Source_Sheet_Title" as a header name if the original sheet didn't have it (it didn't).
    # The consolidate script added it to the DataFrame. 
    # So `df.to_csv` wrote header row 0 with "Source_Sheet_Title".
    # Row 1 (the original subheader) would have the VALUE of that column for the first row of data? 
    # No, row 1 in the CSV is the subheader row. 
    # The consolidate script filled `Source_Sheet_Title` for ALL rows.
    # So row 1 (subheader) acts as a data row for the `Source_Sheet_Title` column?
    # No, header=1 means we use row 1 as labels. 
    # The value at row 1, col X (where Source_Sheet_Title is) will become the NAME of the column.
    # The value of `Source_Sheet_Title` for that row (which is a header row in original sheet) 
    # is actually the title string!
    # So the column name will be something like "Turma A - Grupo 1".
    # This is bad. We need to preserve the source info.
    
    # Retry Strategy:
    # Read with header=0 to get the metadata columns correctly.
    # Then identify the real header (row 1) and merge.
    
    print("\nRe-reading with proper handling...")
    df_raw = pd.read_csv(input_file, header=0)
    
    # Metadata columns are likely at the end
    meta_cols = ['Source_Sheet_Title', 'Source_URL']
    
    # Get metadata for each row (it's repeated)
    # We want to keep these.
    
    # The data starts at row 1 (which contains the subheaders)
    # But we want to use row 1 as headers for the main data.
    
    # Extract the subheader row values
    subheaders = df_raw.iloc[0].values
    
    # Create valid column names
    # Combining Superheader (Row 0) + Subheader (Row 1) might be useful?
    # Or just use Subheader, but keep Meta Cols from Row 0 names.
    
    final_cols = []
    for i, col in enumerate(df_raw.columns):
        if col in meta_cols:
            final_cols.append(col)
        else:
            # Use subheader value if available
            sub_val = subheaders[i]
            if pd.notna(sub_val) and str(sub_val).strip() != '':
                final_cols.append(str(sub_val).strip())
            else:
                # Fallback to superheader or index
                final_cols.append(col if 'Extra' not in col and 'Unnamed' not in col else f"Col_{i}")
    
    # Filter out the subheader row (row 0 in df_raw) from the data
    df_clean = df_raw.iloc[1:].copy()
    df_clean.columns = final_cols
    
    # Now clean names again
    clean_cols = []
    for col in df_clean.columns:
        if col in meta_cols:
            clean_cols.append(col)
        else:
            clean_cols.append(clean_column_name(col))
            
    df_clean.columns = clean_cols
    
    # Save processed
    df_clean.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    print("Final Columns:", df_clean.columns.tolist())

if __name__ == '__main__':
    run_eda()
