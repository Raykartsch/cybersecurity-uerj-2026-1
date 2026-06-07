import pandas as pd
import pathlib
import os

def read_parquet_files(directory_path):
    """
    Reads all parquet files in a directory and returns a concatenated DataFrame.
    """
    path = pathlib.Path(directory_path)
    
    # Find all .parquet files in the directory
    parquet_files = list(path.glob('*.parquet'))
    
    if not parquet_files:
        print(f"No parquet files found in {directory_path}")
        return None
    
    print(f"Reading {len(parquet_files)} files...")
    
    # Read and concatenate
    try:
        df_list = [pd.read_parquet(file) for file in parquet_files]
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
    except Exception as e:
        print(f"Error reading parquet files: {e}")
        return None

if __name__ == "__main__":
    # Update this path to your parquet directory
    default_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    target_dir = os.path.join(default_path, "final-project/db")
    df = read_parquet_files(target_dir)
    
    if df is not None:
        print("\nSuccess! Data Preview:")
        print(df.head())
        print(f"\nTotal rows: {len(df)}")
