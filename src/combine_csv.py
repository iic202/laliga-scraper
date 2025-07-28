import pandas as pd
import glob
import os

def combine_csvs(directory_path=".", output_file="combined.csv", add_source_column=False):
   
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in the directory!")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for file in sorted(csv_files):
        print(f"  - {os.path.basename(file)}")
    
    dataframes = []
    for file in sorted(csv_files):
        try:
            df = pd.read_csv(file)
            if add_source_column:
                df['source_file'] = os.path.basename(file)
            dataframes.append(df)
        except Exception as e:
            print(f"✗ Error loading {file}: {e}")
    
    if not dataframes:
        print("No valid CSV files could be loaded!")
        return

    print("\nCombining files...")
    combined_df = pd.concat(dataframes, ignore_index=True)

    full_output_path = os.path.join("data/laliga", output_file)
    combined_df.to_csv(full_output_path, index=False)

    print(f"\n[+] Successfully combined {len(csv_files)} files into '{full_output_path}'")
    print(f"Total rows: {len(combined_df)}")
    print(f"Columns: {list(combined_df.columns)}")

if __name__ == "__main__":
    combine_csvs()