"""
ETL Process Script for CMS Open Payments Data

Processes large CSV file (15M+ rows) using chunked reading to:
1. Filter: Keep only Physicians, exclude Teaching Hospitals, drop null NPIs
2. Clean: Convert dates, validate amounts
3. Aggregate: Calculate RFM values in-memory
4. Load: Batch insert into SQLite database

Usage:
    python -m scripts.etl_process
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any
import time

import pandas as pd
from tqdm import tqdm
from sqlalchemy.orm import Session

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import Doctor, PaymentRecord, Base
from app.config import get_settings

# ============== Configuration ==============

settings = get_settings()

# Source CSV file path
CSV_FILE_PATH = settings.raw_data_path

# Processing parameters
CHUNK_SIZE = 50000  # Process 50k rows at a time
IMPORT_DETAILS = False  # Set to True to import PaymentRecord details (WARNING: 15M rows!)

# Reference date for Recency calculation (use latest date in dataset or current date)
REFERENCE_DATE = datetime(2025, 6, 30).date()  # Based on Payment_Publication_Date

# ============== Core Fields Mapping ==============

CORE_FIELDS = [
    'Covered_Recipient_NPI',
    'Covered_Recipient_First_Name',
    'Covered_Recipient_Last_Name',
    'Covered_Recipient_Primary_Type_1',
    'Covered_Recipient_Specialty_1',
    'Recipient_State',
    'Total_Amount_of_Payment_USDollars',
    'Date_of_Payment',
    'Nature_of_Payment_or_Transfer_of_Value',
    'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name',
    'Name_of_Drug_or_Biological_or_Device_or_Medical_Supply_1',
    'Covered_Recipient_Type'  # For filtering
]


class ETLProcessor:
    """ETL Processor for CMS Open Payments data."""
    
    def __init__(self):
        self.doctor_stats: Dict[str, Dict[str, Any]] = {}
        self.total_rows = 0
        self.valid_rows = 0
        self.filtered_rows = 0
        self.error_rows = 0
        self.payment_batch = []
        
    def filter_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """
        Filter chunk to keep only valid physician records.
        
        Filters:
        1. Keep only Physicians (exclude Teaching Hospitals)
        2. Drop rows with null NPI
        3. Keep only rows with Primary_Type containing "Physician"
        """
        initial_count = len(chunk)
        
        # Filter 1: Exclude Teaching Hospitals (keep only individual recipients)
        chunk = chunk[
            chunk['Covered_Recipient_Type'].isin([
                'Covered Recipient Physician',
                'Covered Recipient Non-Physician Practitioner'
            ])
        ]
        
        # Filter 2: Drop null NPIs
        chunk = chunk.dropna(subset=['Covered_Recipient_NPI'])
        
        # Filter 3: Keep only Physicians (Primary_Type contains "Physician")
        # Note: Some Non-Physician Practitioners might be valuable too, adjust as needed
        chunk = chunk[
            chunk['Covered_Recipient_Primary_Type_1'].str.contains(
                'Physician|Doctor|Osteopathy',
                case=False,
                na=False
            )
        ]
        
        filtered_count = initial_count - len(chunk)
        self.filtered_rows += filtered_count
        
        return chunk
    
    def clean_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform data.
        
        Transformations:
        1. Convert Date_of_Payment to datetime
        2. Ensure Total_Amount is float
        3. Handle missing values
        """
        # Convert date (format: MM/DD/YYYY)
        try:
            chunk['Date_of_Payment'] = pd.to_datetime(
                chunk['Date_of_Payment'],
                format='%m/%d/%Y',
                errors='coerce'
            )
        except Exception as e:
            print(f"Warning: Date conversion error: {e}")
            chunk['Date_of_Payment'] = pd.to_datetime(chunk['Date_of_Payment'], errors='coerce')
        
        # Ensure amount is float
        chunk['Total_Amount_of_Payment_USDollars'] = pd.to_numeric(
            chunk['Total_Amount_of_Payment_USDollars'],
            errors='coerce'
        ).fillna(0.0)
        
        # Convert NPI to string (remove .0 from float representation)
        chunk['Covered_Recipient_NPI'] = chunk['Covered_Recipient_NPI'].astype(int).astype(str)
        
        # Drop rows with invalid dates
        chunk = chunk.dropna(subset=['Date_of_Payment'])

        # Clean Specialty: Remove redundant prefix (keep content after first '|')
        # Example: 'Allopathic & Osteopathic Physicians|Internal Medicine|Cardiovascular Disease' -> 'Internal Medicine|Cardiovascular Disease'
        if 'Covered_Recipient_Specialty_1' in chunk.columns:
            chunk['Covered_Recipient_Specialty_1'] = chunk['Covered_Recipient_Specialty_1'].apply(
                lambda x: x.split('|', 1)[1] if isinstance(x, str) and '|' in x else x
            )
        
        return chunk
    
    def aggregate_rfm(self, chunk: pd.DataFrame):
        """
        Aggregate RFM values in memory.
        
        For each NPI:
        - R (Recency): Days since most recent payment
        - F (Frequency): Count of payment records
        - M (Monetary): Sum of payment amounts
        """
        for _, row in chunk.iterrows():
            try:
                npi = row['Covered_Recipient_NPI']
                amount = row['Total_Amount_of_Payment_USDollars']
                payment_date = row['Date_of_Payment'].date()
                
                if npi not in self.doctor_stats:
                    # Initialize doctor record
                    self.doctor_stats[npi] = {
                        'npi': npi,
                        'first_name': row.get('Covered_Recipient_First_Name'),
                        'last_name': row.get('Covered_Recipient_Last_Name'),
                        'primary_type': row.get('Covered_Recipient_Primary_Type_1'),
                        'specialty': row.get('Covered_Recipient_Specialty_1'),
                        'state': row.get('Recipient_State'),
                        'most_recent_date': payment_date,
                        'frequency': 0,
                        'monetary': 0.0
                    }
                
                # Update RFM values
                stats = self.doctor_stats[npi]
                
                # Update most recent date (for Recency)
                if payment_date > stats['most_recent_date']:
                    stats['most_recent_date'] = payment_date
                
                # Update Frequency
                stats['frequency'] += 1
                
                # Update Monetary
                stats['monetary'] += amount
                
                self.valid_rows += 1
                
            except Exception as e:
                self.error_rows += 1
                if self.error_rows <= 10:  # Only print first 10 errors
                    print(f"Error processing row: {e}")
    
    def load_payment_details(self, chunk: pd.DataFrame, db: Session):
        """
        Load payment details to database (optional, for detailed analysis).
        WARNING: This will insert millions of records!
        """
        if not IMPORT_DETAILS:
            return
        
        for _, row in chunk.iterrows():
            try:
                payment_record = {
                    'npi': row['Covered_Recipient_NPI'],
                    'amount': row['Total_Amount_of_Payment_USDollars'],
                    'payment_date': row['Date_of_Payment'].date(),
                    'payment_type': row.get('Nature_of_Payment_or_Transfer_of_Value'),
                    'manufacturer_name': row.get('Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name'),
                    'product_name': row.get('Name_of_Drug_or_Biological_or_Device_or_Medical_Supply_1')
                }
                self.payment_batch.append(payment_record)
                
                # Batch insert every 10k records
                if len(self.payment_batch) >= 10000:
                    db.bulk_insert_mappings(PaymentRecord, self.payment_batch)
                    db.commit()
                    self.payment_batch = []
                    
            except Exception as e:
                self.error_rows += 1
    
    def process_csv(self):
        """Main processing pipeline."""
        print("="*60)
        print("CMS Open Payments ETL Process")
        print("="*60)
        print(f"Source File: {CSV_FILE_PATH}")
        print(f"Chunk Size: {CHUNK_SIZE:,}")
        print(f"Import Details: {IMPORT_DETAILS}")
        print(f"Reference Date: {REFERENCE_DATE}")
        print("="*60)
        
        start_time = time.time()
        
        # Get total rows for progress bar
        print("Counting total rows...")
        total_rows = sum(1 for _ in open(CSV_FILE_PATH, encoding='utf-8')) - 1
        print(f"Total rows: {total_rows:,}")
        
        # Process CSV in chunks
        db = SessionLocal()
        
        try:
            chunk_iterator = pd.read_csv(
                CSV_FILE_PATH,
                chunksize=CHUNK_SIZE,
                usecols=CORE_FIELDS,
                low_memory=False
            )
            
            with tqdm(total=total_rows, desc="Processing", unit="rows") as pbar:
                for chunk in chunk_iterator:
                    self.total_rows += len(chunk)
                    
                    # Pipeline: Filter -> Clean -> Aggregate
                    chunk = self.filter_chunk(chunk)
                    chunk = self.clean_chunk(chunk)
                    self.aggregate_rfm(chunk)
                    
                    # Optional: Load payment details
                    if IMPORT_DETAILS:
                        self.load_payment_details(chunk, db)
                    
                    pbar.update(len(chunk))
            
            # Insert remaining payment records
            if IMPORT_DETAILS and self.payment_batch:
                db.bulk_insert_mappings(PaymentRecord, self.payment_batch)
                db.commit()
            
            # Calculate Recency and insert Doctor records
            print("\nCalculating RFM values and inserting doctors...")
            doctor_records = []
            
            for npi, stats in tqdm(self.doctor_stats.items(), desc="Preparing doctors"):
                recency_days = (REFERENCE_DATE - stats['most_recent_date']).days
                
                doctor_records.append({
                    'npi': stats['npi'],
                    'first_name': stats['first_name'],
                    'last_name': stats['last_name'],
                    'primary_type': stats['primary_type'],
                    'specialty': stats['specialty'],
                    'state': stats['state'],
                    'recency_days': recency_days,
                    'frequency': stats['frequency'],
                    'monetary': stats['monetary']
                })
            
            # Batch insert doctors
            print(f"Inserting {len(doctor_records):,} doctor records...")
            db.bulk_insert_mappings(Doctor, doctor_records)
            db.commit()
            
        except Exception as e:
            print(f"\nERROR: {e}")
            db.rollback()
            raise
        finally:
            db.close()
        
        # Print statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("ETL Process Complete!")
        print("="*60)
        print(f"Total rows processed: {self.total_rows:,}")
        print(f"Valid rows: {self.valid_rows:,}")
        print(f"Filtered rows: {self.filtered_rows:,}")
        print(f"Error rows: {self.error_rows:,}")
        print(f"Unique doctors (NPIs): {len(self.doctor_stats):,}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print("="*60)
        
        # Print sample statistics
        if self.doctor_stats:
            print("\nSample RFM Statistics:")
            df_stats = pd.DataFrame(list(self.doctor_stats.values()))
            print(f"Recency (days): min={df_stats['most_recent_date'].min()}, max={df_stats['most_recent_date'].max()}")
            print(f"Frequency: mean={df_stats['frequency'].mean():.2f}, median={df_stats['frequency'].median():.0f}")
            print(f"Monetary: mean=${df_stats['monetary'].mean():.2f}, median=${df_stats['monetary'].median():.2f}")


def main():
    """Main entry point."""
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"ERROR: CSV file not found: {CSV_FILE_PATH}")
        print("Please update the path in app/config.py")
        sys.exit(1)
    
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    # Run ETL
    processor = ETLProcessor()
    processor.process_csv()


if __name__ == "__main__":
    main()
