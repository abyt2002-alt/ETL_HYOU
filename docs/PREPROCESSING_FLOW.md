# Preprocessing Flow Documentation

## Overview

The preprocessing layer is the second major module of the platform. It reads from raw PostgreSQL tables (populated by ingestion), applies source-specific cleaning and enrichment, and writes to curated tables suitable for downstream reporting.

## Architecture

### Components

1. **Preprocessing Service** - Orchestrates preprocessing operations
2. **Quality Service** - Performs data quality checks and duplicate detection
3. **Mapping Service** - Manages external mapping files for DMA enrichment
4. **Labeling Service** - Applies source labels to GA session sources
5. **Curated Writer Service** - Writes processed data to curated tables

### Database Tables

**Operational Tables:**
- `preprocessing_runs` - Tracks preprocessing run executions
- `preprocessing_run_items` - Tracks individual source preprocessing within a run
- `data_quality_issues` - Logs data quality problems
- `mapping_files` - Registry of external mapping files

**Curated Tables:**
- `curated_shopify` - Cleaned Shopify data with DMA enrichment
- `curated_ga` - Cleaned GA data with DMA enrichment and source labels
- `curated_gads` - Cleaned Google Ads data
- `curated_meta` - Cleaned Meta data

## Source-Specific Preprocessing

### Shopify

**Input:** `raw_shopify`  
**Output:** `curated_shopify`  
**Mapping Required:** Yes (shopify_dma)

**Processing Steps:**
1. Load raw data from PostgreSQL
2. Clean postal code (trim, take first token before hyphen)
3. Load active Shopify DMA mapping file
4. Clean mapping zip codes using same logic
5. Deduplicate mapping on zip key
6. Left join source to mapping on cleaned zip
7. Create DMA column from mapping
8. Check exact duplicates
9. Check business duplicates (day + order + shipping_postal_code)
10. Run data quality checks
11. Write to curated_shopify

**Mapping File:**
- Expected file: `pincode_mappings 1.csv`
- Required columns: `Zip Code`, `DMA Description`
- Purpose: Postal code → DMA enrichment

### Google Analytics

**Input:** `raw_ga`  
**Output:** `curated_ga`  
**Mapping Required:** Yes (ga_dma)

**Processing Steps:**
1. Load raw data from PostgreSQL
2. Normalize city and region (lowercase, trim)
3. Load active GA DMA mapping file
4. Normalize mapping city and region
5. Deduplicate mapping on city + region
6. Left join source to mapping
7. Create DMA column
8. Apply source labeling rules to session_source
9. Check exact duplicates
10. Check business duplicates (day + city + region + session_source)
11. Run data quality checks
12. Write to curated_ga

**Mapping File:**
- Expected file: `Final DMA mapping for GA.xlsx`
- Required columns: `City`, `Region`, `DMA`
- Purpose: City + Region → DMA enrichment

**Source Labeling:**
- Meta: facebook, fb, instagram, ig, meta
- Google: google, gclid, adwords, ads, youtube, yt
- Unlabeled: everything else

### Google Ads

**Input:** `raw_gads`  
**Output:** `curated_gads`  
**Mapping Required:** No

**Processing Steps:**
1. Load raw data from PostgreSQL
2. Rename `impr_` to `impr`
3. Check exact duplicates
4. Check business duplicates (day + campaign)
5. Run data quality checks
6. Write to curated_gads

### Meta

**Input:** `raw_meta`  
**Output:** `curated_meta`  
**Mapping Required:** No

**Processing Steps:**
1. Load raw data from PostgreSQL
2. Check exact duplicates
3. Check business duplicates (day + dma_region)
4. Run data quality checks
5. Write to curated_meta

## Data Quality Checks

### Checks Performed

1. **Missing Required Columns** - Fails preprocessing if strict mode enabled
2. **Null Values** - Counts nulls in required columns
3. **Invalid Dates** - Detects unparseable date values
4. **Invalid Numerics** - Detects non-numeric values in numeric columns
5. **Exact Duplicates** - Finds rows that are identical across all columns
6. **Business Duplicates** - Finds rows with duplicate business keys
7. **Mapping Unmatched** - Counts rows that didn't match mapping file

### Duplicate Types

**Exact Duplicates:**
- Rows that are identical across ALL columns
- Configurable: can be dropped or kept
- Default: dropped before writing to curated table

**Business Duplicates:**
- Rows with duplicate business keys (source-specific)
- Always logged and counted
- Not automatically dropped (requires business decision)

### Issue Severity

- **Error** - Missing required columns, invalid schema
- **Warning** - Business duplicates, mapping unmatched, unlabeled sources

## Mapping File Management

### Upload Process

1. User uploads CSV or Excel file via API
2. System validates file format and required columns
3. File saved to `/app/mapping_files/` with timestamp
4. File registered in `mapping_files` table
5. User activates file (deactivates previous active file)
6. Preprocessing uses active file for enrichment

### Mapping Types

- `shopify_dma` - Shopify postal code to DMA mapping
- `ga_dma` - GA city + region to DMA mapping

### Activation Rules

- Only one active mapping file per type at a time
- Activating a new file deactivates the previous one
- Preprocessing runs record which mapping file was used

## API Endpoints

### Preprocessing Operations

- `GET /api/preprocessing/sources` - List available sources
- `POST /api/preprocessing/run/all` - Run all sources
- `POST /api/preprocessing/run/{source}` - Run single source
- `GET /api/preprocessing/runs/latest` - Get latest run
- `GET /api/preprocessing/runs` - List run history
- `GET /api/preprocessing/runs/{id}` - Get run details
- `GET /api/preprocessing/curated/{table}` - Preview curated data

### Mapping File Operations

- `GET /api/mapping-files` - List all mapping files
- `POST /api/mapping-files/upload` - Upload new mapping file
- `POST /api/mapping-files/{id}/activate` - Activate mapping file
- `GET /api/mapping-files/{id}/preview` - Preview mapping file
- `GET /api/mapping-files/active/{type}` - Get active mapping file

### Quality Operations

- `GET /api/quality/issues` - List all quality issues
- `GET /api/quality/issues/run-item/{id}` - Get issues for run item

## Configuration

Preprocessing behavior is defined in `backend/app/preprocessing_config.py`:

```python
PreprocessingConfig(
    source_name="shopify",
    raw_table_name="raw_shopify",
    curated_table_name="curated_shopify",
    required_columns=["day", "shipping_postal_code", "order"],
    optional_columns=[...],
    date_columns=["day"],
    numeric_columns=["net_sales", ...],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "order", "shipping_postal_code"],
    mapping_required=True,
    mapping_type="shopify_dma",
    drop_exact_duplicates=True,
    strict_required_columns=True,
    output_columns=[...]
)
```

## Adding a New Source

1. Add configuration to `preprocessing_config.py`
2. Create curated table model in `models.py`
3. Create migration for curated table
4. Add source-specific preprocessing logic in `preprocessing_service.py`
5. Update frontend to display new source

## Current Scope

**Implemented:**
- Config-driven preprocessing per source
- DMA enrichment for Shopify and GA
- Source labeling for GA
- Exact and business duplicate detection
- Data quality checks and issue logging
- Mapping file upload and management
- Curated table persistence
- Run tracking and history
- API endpoints for all operations

**Not Yet Implemented:**
- Authentication/authorization for mapping file uploads
- Automated scheduling of preprocessing runs
- Advanced anomaly detection
- Data lineage visualization
- Comprehensive automated tests
- Retry logic for failed sources
- Monitoring and alerting
- Incremental preprocessing (currently full replace)

## Operational Notes

- Preprocessing reads from raw tables only (never from Google Sheets)
- Curated tables are truncated and reloaded on each run (replace mode)
- Mapping files are external assets, not in code repository
- Each preprocessing run records which mapping file version was used
- Failed preprocessing of one source doesn't block others in run-all mode
- Quality issues are logged but don't always fail preprocessing (depends on severity)
