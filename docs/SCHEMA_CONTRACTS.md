# Schema Contracts

This document defines the contract between Google Sheet tabs and PostgreSQL tables.

## Load Strategy

**Default Mode**: Replace (truncate and reload)

All sources use **replace mode** by default to prevent duplicate data on repeated runs. Google Sheets contain current state, not incremental changes, so truncating and reloading is the appropriate strategy.

**Alternative**: Upsert mode (structure exists, not fully tested) for large datasets with reliable unique keys.

---

## Meta Source

**Sheet Tab**: `Meta`

**Target Table**: `raw_meta`

**Load Mode**: Replace (truncate before each load)

**Expected Columns**:
| Sheet Column | Type | Required | Database Column | Database Type |
|--------------|------|----------|-----------------|---------------|
| Day | Date | Yes | day | DATE |
| DMA region | String | Yes | dma_region | VARCHAR(255) |
| Impressions | Integer | Yes | impressions | INTEGER |
| Amount spent | Numeric | Yes | amount_spent | NUMERIC(10,2) |

**Ingestion Rules**:
- Load mode: Replace (truncate table, then insert)
- Date conversion: Excel serial dates converted to DATE
- Null handling: Numeric nulls preserved, integer nulls become 0
- Column mapping: Spaces replaced with underscores, lowercased
- Extra columns: Logged as warning, ignored during load
- Strict mode: Disabled (unexpected columns don't fail ingestion)

---

## Shopify Source

**Sheet Tab**: `Shopify`

**Target Table**: `raw_shopify`

**Load Mode**: Replace (truncate before each load)

**Expected Columns**:
| Sheet Column | Type | Required | Database Column | Database Type |
|--------------|------|----------|-----------------|---------------|
| Day | Date | Yes | day | DATE |
| Shipping postal code | String | Yes | shipping_postal_code | VARCHAR(50) |
| Order | String | Yes | order | VARCHAR(100) |
| Customer type | String | Yes | customer_type | VARCHAR(100) |
| Net sales | Numeric | Yes | net_sales | NUMERIC(10,2) |
| Order item current quantity | Integer | Yes | order_item_current_quantity | INTEGER |
| Orders | Integer | Yes | orders | INTEGER |

**Ingestion Rules**:
- Load mode: Replace (truncate table, then insert)
- Date conversion: Excel serial dates converted to DATE
- Null handling: Numeric nulls preserved, integer nulls become 0
- Column mapping: Spaces replaced with underscores, lowercased
- Extra columns: Logged as warning, ignored during load
- Strict mode: Disabled (unexpected columns don't fail ingestion)

---

## GA (Google Analytics) Source

**Sheet Tab**: `GA`

**Target Table**: `raw_ga`

**Load Mode**: Replace (truncate before each load)

**Expected Columns**:
| Sheet Column | Type | Required | Database Column | Database Type |
|--------------|------|----------|-----------------|---------------|
| Day | Date | Yes | day | DATE |
| Region | String | Yes | region | VARCHAR(255) |
| Session source | String | Yes | session_source | VARCHAR(255) |
| City | String | Yes | city | VARCHAR(255) |
| Sessions | Integer | Yes | sessions | INTEGER |

**Ingestion Rules**:
- Load mode: Replace (truncate table, then insert)
- Date conversion: Excel serial dates converted to DATE
- Null handling: Integer nulls become 0
- Column mapping: Spaces replaced with underscores, lowercased
- Extra columns: Logged as warning, ignored during load
- Strict mode: Disabled (unexpected columns don't fail ingestion)

---

## GAds (Google Ads) Source

**Sheet Tab**: `GAds`

**Target Table**: `raw_gads`

**Load Mode**: Replace (truncate before each load)

**Expected Columns**:
| Sheet Column | Type | Required | Database Column | Database Type |
|--------------|------|----------|-----------------|---------------|
| Campaign | String | Yes | campaign | VARCHAR(255) |
| Day | Date | Yes | day | DATE |
| Cost | Numeric | Yes | cost | NUMERIC(10,2) |
| Impr | Integer | Yes | impr | INTEGER |

**Ingestion Rules**:
- Load mode: Replace (truncate table, then insert)
- Date conversion: Excel serial dates converted to DATE
- Null handling: Numeric nulls preserved, integer nulls become 0
- Column mapping: Spaces replaced with underscores, lowercased
- Extra columns: Logged as warning, ignored during load
- Strict mode: Disabled (unexpected columns don't fail ingestion)

---

## Common Ingestion Rules

### Date Handling

Excel date values can be:
1. **Excel serial numbers** (e.g., 44927): Converted using base date 1899-12-30
2. **String dates** (e.g., "2024-01-15", "01/15/2024"): Parsed with multiple format attempts
3. **Python datetime objects**: Used directly

All dates are converted to PostgreSQL DATE type.

### Type Coercion

**Integer Fields**:
- Coerced using `pd.to_numeric(errors='coerce')`
- NaN values filled with 0
- Cast to integer type

**Numeric Fields**:
- Coerced using `pd.to_numeric(errors='coerce')`
- NaN values preserved as NULL in database
- Stored as NUMERIC(10,2)

**String Fields**:
- No coercion applied
- Stored as-is
- Truncated if exceeding column length

### Column Name Normalization

Sheet column names are normalized for database:
1. Convert to lowercase
2. Replace spaces with underscores
3. Remove special characters (if any)

Example: `"DMA region"` → `"dma_region"`

### Validation

Before ingestion, the system validates:
1. **Required columns present**: All columns in `required_columns` must exist
2. **Unexpected columns**: Extra columns logged as warning, then ignored
3. **Data not empty**: At least one row must be present

### Error Handling

**Column Validation Failures**:
- Missing required columns → Fail immediately, no data loaded
- Unexpected columns (default) → Log warning, ignore columns, continue
- Unexpected columns (strict mode) → Fail immediately, no data loaded

**Type Coercion Failures**:
- Invalid dates → Converted to NULL
- Invalid numbers → Converted to NULL (or 0 for integers)
- Invalid strings → Preserved as-is

**Load Failures**:
- Database constraint violations → Entire batch fails
- Connection errors → Retry not implemented, manual re-run required

### Metadata

All tables include:
- `id`: Auto-incrementing primary key
- `ingested_at`: Timestamp of when row was loaded (default: current UTC time)

### Load Modes

**Replace Mode** (default for all sources):
- Truncates table before loading
- Prevents duplicate data on repeated runs
- Suitable for Google Sheets (current state, not incremental)
- Acceptable for datasets < 100K rows
- No unique keys required

**Upsert Mode** (configurable, not fully tested):
- Updates existing records based on unique keys
- Inserts new records
- Preserves historical data not in current sheet
- Requires `unique_keys` configuration
- Suitable for large datasets or when preserving history

### Strict Column Mode

**Default Behavior** (`strict_columns=False`):
- Unexpected columns logged as warning
- Extra columns ignored during transformation
- Ingestion continues successfully

**Strict Mode** (`strict_columns=True`):
- Unexpected columns cause hard failure
- No data loaded for that source
- Error message specifies unexpected columns
- Use when sheet structure must match exactly

---

## Adding New Sources

To add a new source, define:

1. **Sheet tab name**: Exact name of the tab in Google Sheets
2. **Required columns**: List of column names that must be present
3. **Optional columns**: List of column names that may be present
4. **Field types**: Mapping of column name to type (`string`, `integer`, `numeric`, `date`)
5. **Date fields**: List of columns containing dates
6. **Numeric fields**: List of columns containing decimal numbers
7. **Load mode**: `replace` (default) or `upsert`
8. **Unique keys**: List of columns for upsert mode (if applicable)
9. **Strict columns**: `False` (default) or `True`

Then create the corresponding database table with:
- Normalized column names (lowercase, underscores)
- Appropriate data types
- `id` primary key
- `ingested_at` timestamp

Example:

```python
SourceConfig(
    source_name="new_source",
    sheet_tab_name="NewSourceTab",
    target_table_name="raw_new_source",
    required_columns=["Date", "Metric Name", "Value"],
    optional_columns=["Notes"],
    field_types={
        "Date": "date",
        "Metric Name": "string",
        "Value": "numeric",
        "Notes": "string"
    },
    date_fields=["Date"],
    numeric_fields=["Value"],
    load_mode="replace",  # Truncate and reload
    unique_keys=[],  # Not needed for replace mode
    strict_columns=False  # Warn on unexpected, don't fail
)
```

---

## Load Mode Decision Guide

### Use Replace Mode When:
- Dataset is small to medium (< 100K rows)
- Google Sheet contains current state only
- No need to preserve historical data
- Simplicity is preferred
- No reliable unique keys available

### Use Upsert Mode When:
- Dataset is large (> 100K rows)
- Full reload is too slow
- Need to preserve historical records
- Have reliable unique keys (e.g., transaction ID + date)
- Sheet may contain partial updates

### Not Recommended:
- **Append mode**: Would duplicate data on repeated runs (Google Sheets are not incremental)

---

## Authentication

**Method**: Service Account with JSON credentials

**Not OAuth**: This system uses service account authentication, not OAuth with refresh tokens.

**Setup**:
1. Create Google Cloud project
2. Enable Google Sheets API
3. Create service account
4. Download JSON credentials to `backend/credentials.json`
5. Share sheet with service account email (viewer permission sufficient)

---

## Current Limitations

- **No incremental loading**: Loads entire sheet each time
- **No deduplication**: Replace mode truncates all data
- **No data quality checks**: Only column validation
- **No retry logic**: Failed ingestions must be manually re-run
- **Upsert mode not tested**: Structure exists but not fully implemented

---

## Summary

All sources use **replace mode** by default to prevent duplicate data. This is the appropriate strategy for Google Sheets, which contain current state rather than incremental changes.

Column validation fails on missing required columns but only warns on unexpected extra columns (unless strict mode is enabled). This provides a good balance between data quality and operational flexibility.
