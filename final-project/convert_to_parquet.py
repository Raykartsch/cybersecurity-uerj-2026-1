import pyarrow.csv as pv
import pyarrow.parquet as pq
import argparse
import os
import time

def convert_csv_to_parquet(csv_path, parquet_path):
    print(f"--- Converting {csv_path} to {parquet_path} ---")
    start_time = time.time()
    
    try:
        # pyarrow.csv.read_csv is highly optimized for performance and memory
        # It automatically detects schemas and handles large files well.
        table = pv.read_csv(csv_path)
        
        print(f"Read complete in {time.time() - start_time:.2f} seconds. Writing Parquet...")
        
        # Write to parquet with Snappy compression (default and balanced)
        pq.write_table(table, parquet_path, compression='snappy')
        
        end_time = time.time()
        print(f"Conversion successful!")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Original size: {os.path.getsize(csv_path) / (1024**2):.2f} MB")
        print(f"Parquet size: {os.path.getsize(parquet_path) / (1024**2):.2f} MB")
        
    except Exception as e:
        print(f"Error during conversion: {e}")

def main():
    default_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(default_path, "final-project/db/DNN-EdgeIIoT-dataset.csv")
    parquet_path = os.path.join(default_path, "final-project/db/dnn.parquet")
    convert_csv_to_parquet(csv_path, parquet_path)

if __name__ == "__main__":
    main()
