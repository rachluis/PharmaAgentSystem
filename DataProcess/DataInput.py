import pandas as pd
import os

# File path provided by the user
file_path = r"E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv"

def inspect_csv_columns(path):
    """
    Reads the header and a few rows of the CSV to display field information.
    """
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    output_file = os.path.join(os.path.dirname(path), "columns_info.txt")
    # If the CSV is outside the workspace, save the info in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "columns_info.txt")

    try:
        # Read only the first few rows to get column info without loading the whole file
        df = pd.read_csv(path, nrows=5)
        
        output_lines = []
        output_lines.append(f"Reading file info from: {path}")
        output_lines.append("\n" + "="*50)
        output_lines.append(f"Total Columns: {len(df.columns)}")
        output_lines.append("="*50)
        
        output_lines.append("\n--- Column List ---")
        for i, col in enumerate(df.columns):
            output_lines.append(f"{i}: {col}")
            
        output_lines.append("\n" + "="*50)
        output_lines.append("--- First 5 Rows Sample ---")
        output_lines.append(str(df.head()))
        output_lines.append("="*50)

        output_lines.append("\n--- Inferred Data Types (based on first 5 rows) ---")
        output_lines.append(str(df.dtypes))
        
        # Print to console
        print("\n".join(output_lines))
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"\nColumn info saved to: {output_file}")

    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    inspect_csv_columns(file_path)
