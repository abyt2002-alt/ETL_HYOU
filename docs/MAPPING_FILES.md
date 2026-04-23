# Mapping Files Documentation

## Overview

Mapping files are external operational assets used to enrich raw data with additional dimensions like DMA (Designated Market Area). They are managed separately from code and can be updated without code changes.

## Mapping Types

### 1. Shopify DMA Mapping

**Purpose:** Enrich Shopify data with DMA based on postal code

**Mapping Type:** `shopify_dma`  
**Source:** Shopify  
**Expected File:** `pincode_mappings 1.csv`  
**Format:** CSV or Excel

**Required Columns:**
- `Zip Code` - Postal/ZIP code
- `DMA Description` - DMA name/description

**Join Logic:**
```
Clean source postal code (trim, take first token before hyphen)
Clean mapping zip code (same logic)
Left join on cleaned postal code
```

**Example:**
```csv
Zip Code,DMA Description
10001,New York NY
10002,New York NY
90001,Los Angeles CA
```

### 2. GA DMA Mapping

**Purpose:** Enrich Google Analytics data with DMA based on city and region

**Mapping Type:** `ga_dma`  
**Source:** Google Analytics  
**Expected File:** `Final DMA mapping for GA.xlsx`  
**Format:** CSV or Excel

**Required Columns:**
- `City` - City name
- `Region` - Region/state name
- `DMA` - DMA code or name

**Join Logic:**
```
Normalize source city and region (lowercase, trim)
Normalize mapping city and region (same logic)
Left join on normalized city + region
```

**Example:**
```csv
City,Region,DMA
new york,new york,New York NY
los angeles,california,Los Angeles CA
chicago,illinois,Chicago IL
```

## Mapping File Lifecycle

### 1. Upload

**API Endpoint:** `POST /api/mapping-files/upload`

**Parameters:**
- `file` - CSV or Excel file
- `mapping_name` - Descriptive name
- `source_name` - Source this mapping applies to
- `mapping_type` - Type identifier (shopify_dma, ga_dma)
- `required_columns` - JSON array of required column names
- `uploaded_by` - User identifier
- `notes` - Optional notes

**Process:**
1. File uploaded via API
2. System validates file format
3. System checks required columns exist
4. File saved to `/app/mapping_files/` with timestamp
5. Record created in `mapping_files` table
6. File marked as inactive (not yet used)

### 2. Validation

**Checks Performed:**
- File can be opened and parsed
- Required columns exist
- File is not empty
- File format is supported (CSV or Excel)

**Validation Errors:**
- Missing required columns → Upload rejected
- Unsupported file type → Upload rejected
- Empty file → Upload rejected
- Corrupt file → Upload rejected

### 3. Preview

**API Endpoint:** `GET /api/mapping-files/{id}/preview?rows=10`

**Purpose:** View first N rows before activation

**Returns:**
```json
{
  "columns": ["Zip Code", "DMA Description"],
  "rows": [
    {"Zip Code": "10001", "DMA Description": "New York NY"},
    ...
  ],
  "total_rows": 50000
}
```

### 4. Activation

**API Endpoint:** `POST /api/mapping-files/{id}/activate`

**Process:**
1. Deactivate all other mapping files of same type
2. Activate selected mapping file
3. Future preprocessing runs use this file

**Rules:**
- Only one active mapping file per type
- Activating new file deactivates previous
- Previous files remain in system (audit trail)

### 5. Usage in Preprocessing

**Process:**
1. Preprocessing service checks if mapping required
2. Loads active mapping file for mapping type
3. Applies cleaning/normalization to mapping data
4. Deduplicates mapping on join keys
5. Performs left join with source data
6. Records mapping file ID in run item
7. Counts matched and unmatched rows

## Mapping File Registry

**Table:** `mapping_files`

**Schema:**
```sql
CREATE TABLE mapping_files (
    id SERIAL PRIMARY KEY,
    mapping_name VARCHAR(100),
    source_name VARCHAR(100),
    mapping_type VARCHAR(100),
    file_name VARCHAR(255),
    storage_path VARCHAR(500),
    file_type VARCHAR(50),
    required_columns TEXT,
    is_active INTEGER,
    uploaded_at TIMESTAMP,
    uploaded_by VARCHAR(100),
    notes TEXT
);
```

**Fields:**
- `mapping_name` - Human-readable name
- `source_name` - Source this applies to (shopify, ga)
- `mapping_type` - Type identifier (shopify_dma, ga_dma)
- `file_name` - Original filename
- `storage_path` - Full path to stored file
- `file_type` - csv or excel
- `required_columns` - Comma-separated list
- `is_active` - 1 if active, 0 if inactive
- `uploaded_at` - Upload timestamp
- `uploaded_by` - User who uploaded
- `notes` - Optional notes

## Data Cleaning Rules

### Shopify Postal Code Cleaning

**Source Data:**
```python
df['shipping_postal_code_cleaned'] = (
    df['shipping_postal_code']
    .astype(str)
    .str.strip()
    .str.split('-').str[0]
)
```

**Mapping Data:**
```python
mapping_df['Zip Code'] = (
    mapping_df['Zip Code']
    .astype(str)
    .str.strip()
    .str.split('-').str[0]
)
```

**Examples:**
- `"10001"` → `"10001"`
- `"10001-1234"` → `"10001"`
- `" 10001 "` → `"10001"`

### GA City/Region Normalization

**Source Data:**
```python
df['city_normalized'] = df['city'].astype(str).str.lower().str.strip()
df['region_normalized'] = df['region'].astype(str).str.lower().str.strip()
```

**Mapping Data:**
```python
mapping_df['City'] = mapping_df['City'].astype(str).str.lower().str.strip()
mapping_df['Region'] = mapping_df['Region'].astype(str).str.lower().str.strip()
```

**Examples:**
- `"New York"` → `"new york"`
- `" Los Angeles "` → `"los angeles"`
- `"CHICAGO"` → `"chicago"`

## Deduplication

**Purpose:** Ensure one-to-one mapping from join key to DMA

**Shopify:**
```python
mapping_df = mapping_df.drop_duplicates(subset=['Zip Code'], keep='first')
```

**GA:**
```python
mapping_df = mapping_df.drop_duplicates(subset=['City', 'Region'], keep='first')
```

**Behavior:**
- If multiple rows have same join key, keep first occurrence
- Prevents one-to-many joins
- Ensures deterministic results

## Mapping Statistics

**Tracked Per Run:**
- `mapping_matches` - Rows that matched mapping file
- `mapping_unmatched` - Rows that didn't match

**Example:**
```
Shopify preprocessing:
- Rows read: 1000
- Mapping matches: 950
- Mapping unmatched: 50
- Match rate: 95%
```

**Interpretation:**
- High unmatched rate → Mapping file may be outdated
- Zero matches → Mapping file may be wrong or corrupted
- 100% matches → Ideal scenario

## API Examples

### Upload Mapping File

```bash
curl -X POST http://localhost:8000/api/mapping-files/upload \
  -F "file=@pincode_mappings.csv" \
  -F "mapping_name=Shopify DMA Mapping 2024" \
  -F "source_name=shopify" \
  -F "mapping_type=shopify_dma" \
  -F "required_columns=[\"Zip Code\",\"DMA Description\"]" \
  -F "uploaded_by=admin"
```

### List Mapping Files

```bash
curl http://localhost:8000/api/mapping-files?mapping_type=shopify_dma
```

### Activate Mapping File

```bash
curl -X POST http://localhost:8000/api/mapping-files/5/activate?mapping_type=shopify_dma
```

### Preview Mapping File

```bash
curl http://localhost:8000/api/mapping-files/5/preview?rows=10
```

## Best Practices

1. **Version mapping files** - Include date or version in mapping_name
2. **Preview before activation** - Always preview to verify data
3. **Keep old files** - Don't delete, maintain audit trail
4. **Monitor match rates** - Track mapping_unmatched over time
5. **Update regularly** - As new postal codes/cities appear
6. **Document sources** - Use notes field to record where mapping came from
7. **Test with small dataset** - Before activating for production runs

## Troubleshooting

### Low Match Rate

**Symptoms:** High `mapping_unmatched` count

**Possible Causes:**
- Mapping file outdated
- Different formatting (spaces, case, special characters)
- Wrong mapping file activated
- Source data has new values not in mapping

**Solutions:**
- Update mapping file with new values
- Check data cleaning logic
- Verify correct mapping file is active

### Zero Matches

**Symptoms:** `mapping_matches = 0`

**Possible Causes:**
- Wrong mapping file activated
- Column names don't match expected
- Data types incompatible
- Mapping file corrupted

**Solutions:**
- Preview mapping file to verify structure
- Check required columns match actual columns
- Reupload mapping file
- Verify mapping type is correct

### Duplicate DMAs

**Symptoms:** Same source row appears multiple times in curated table

**Possible Causes:**
- Mapping file not deduplicated
- One-to-many relationship in mapping

**Solutions:**
- System automatically deduplicates mapping
- If issue persists, check mapping file for true duplicates
- Clean mapping file before upload

## Future Enhancements

- Mapping file versioning with rollback
- Automated mapping file validation on schedule
- Mapping file diff tool (compare two versions)
- Bulk upload of multiple mapping files
- Mapping file expiration dates
- Automated alerts for low match rates
