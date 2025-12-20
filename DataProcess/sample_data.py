import csv
import random
import os

def sample_csv(input_path, output_path, sample_size=2000):
    print(f"Reading from: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return

    try:
        # Try finding the approximate number of lines first? No, straightforward reservoir sampling is fine for single pass.
        with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader)
            except StopIteration:
                print("Error: Empty file")
                return

            reservoir = []
            
            # Fill reservoir
            for i, row in enumerate(reader):
                if i < sample_size:
                    reservoir.append(row)
                else:
                    # Replace elements with gradually decreasing probability
                    j = random.randint(0, i)
                    if j < sample_size:
                        reservoir[j] = row
                
                if (i + 1) % 100000 == 0:
                    print(f"Processed {i + 1} rows...", end='\r')

        print(f"\nFinished processing. Writing {len(reservoir)} rows to {output_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(reservoir)
            
        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Using raw strings for paths to avoid escape character issues
    input_file = r"E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv"
    output_file = r"e:\PharmaAgentSystem\DataProcess\data_sample.csv"
    
    sample_csv(input_file, output_file)
