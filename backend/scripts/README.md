# ETL Process - Usage Guide

## Overview

The ETL script (`backend/scripts/etl_process.py`) processes the large CMS Open Payments CSV file (15M+ rows) and imports cleaned data into the SQLite database.

## Features

- **Chunked Processing**: Reads CSV in 50k row chunks to avoid memory issues
- **Physician Filtering**: Keeps only individual physicians, excludes Teaching Hospitals
- **Data Cleaning**: Converts dates, validates amounts, handles missing values
- **RFM Aggregation**: Calculates Recency, Frequency, Monetary values in-memory
- **Batch Insertion**: Efficiently inserts doctor records using bulk operations

## Configuration

Edit `backend/app/config.py` to set:

- `raw_data_path`: Path to your CSV file (default: `E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv`)

Edit `backend/scripts/etl_process.py` to adjust:

- `CHUNK_SIZE`: Number of rows per chunk (default: 50,000)
- `IMPORT_DETAILS`: Set to `True` to import PaymentRecord details (WARNING: 15M rows!)
- `REFERENCE_DATE`: Date for Recency calculation (default: 2025-06-30)

## Usage

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run ETL Process

```bash
cd backend
python -m scripts.etl_process
```

## Output

The script will:

1. Display progress bar during processing
2. Print statistics:
   - Total rows processed
   - Valid rows (physicians)
   - Filtered rows (Teaching Hospitals, null NPIs)
   - Error rows
   - Unique doctors (NPIs)
   - Processing time
3. Insert doctor records into `pharma.db`

## Expected Processing Time

- **15M rows**: ~10-20 minutes (depends on CPU/disk speed)
- **Memory usage**: ~2-3 GB (for in-memory RFM aggregation)

## Troubleshooting

### File Not Found

- Check `raw_data_path` in `backend/app/config.py`
- Ensure CSV file exists at specified location

### Memory Error

- Reduce `CHUNK_SIZE` in `etl_process.py`
- Close other applications

### Database Locked

- Ensure no other process is accessing `pharma.db`
- Close any SQLite browser tools

## Next Steps

After ETL completes:

1. Verify data: `SELECT COUNT(*) FROM doctors;`
2. Check RFM values: `SELECT AVG(recency_days), AVG(frequency), AVG(monetary) FROM doctors;`
3. Proceed to K-Means clustering analysis
