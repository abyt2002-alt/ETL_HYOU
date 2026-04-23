# Data Quality Rules

## Overview

The preprocessing layer performs comprehensive data quality checks to ensure curated data meets business requirements.

## Quality Check Types

### 1. Missing Required Columns

**Check:** Verify all required columns exist in raw data  
**Severity:** Error  
**Behavior:** Fails preprocessing if `strict_required_columns=True`  
**Example:** Shopify data missing "order" column

### 2. Null Values in Key Fields

**Check:** Count null values in required columns  
**Severity:** Warning  
**Behavior:** Logged but doesn't fail preprocessing  
**Example:** 50 rows with null "shipping_postal_code"

### 3. Invalid Date Values

**Check:** Verify date columns can be parsed  
**Severity:** Warning  
**Behavior:** Logged, invalid dates become null  
**Example:** "day" column contains "invalid-date"

### 4. Invalid Numeric Values

**Check:** Verify numeric columns contain valid numbers  
**Severity:** Warning  
**Behavior:** Logged, invalid values become null  
**Example:** "net_sales" contains "N/A"

### 5. Exact Duplicates

**Check:** Find rows identical across ALL columns  
**Severity:** Warning  
**Behavior:** Counted and optionally dropped  
**Configuration:** `drop_exact_duplicates=True/False`  
**Example:** Two identical rows with same day, order, postal code, sales amount

**Detection Logic:**
```python
duplicate_count = df.duplicated().sum()
deduplicated_df = df.drop_duplicates()
```

### 6. Business Duplicates

**Check:** Find rows with duplicate business keys  
**Severity:** Warning  
**Behavior:** Counted and logged, NOT automatically dropped  
**Configuration:** `duplicate_business_keys=[...]`

**Source-Specific Business Keys:**
- Shopify: `["day", "order", "shipping_postal_code"]`
- GA: `["day", "city", "region", "session_source"]`
- GAds: `["day", "campaign"]`
- Meta: `["day", "dma_region"]`

**Example:** Two rows with same day and order but different sales amounts

**Detection Logic:**
```python
duplicates = df[df.duplicated(subset=business_keys, keep=False)]
duplicate_count = len(duplicates)
```

### 7. Mapping Unmatched Rows

**Check:** Count rows that didn't match mapping file  
**Severity:** Warning  
**Behavior:** Logged, unmatched rows have null DMA  
**Example:** 100 Shopify rows with postal codes not in mapping file

## Exact vs Business Duplicates

### Exact Duplicates

**Definition:** Rows that are 100% identical across every column

**Example:**
```
day        | order | postal | sales
2024-01-01 | 123   | 10001  | 50.00
2024-01-01 | 123   | 10001  | 50.00  <- Exact duplicate
```

**Handling:**
- Configurable: can be automatically dropped
- Default behavior: drop before writing to curated table
- Safe to remove (no information loss)

### Business Duplicates

**Definition:** Rows with duplicate business keys but different data

**Example:**
```
day        | order | postal | sales
2024-01-01 | 123   | 10001  | 50.00
2024-01-01 | 123   | 10001  | 75.00  <- Business duplicate (different sales)
```

**Handling:**
- Always logged and counted
- NOT automatically dropped
- Requires business decision (which row is correct?)
- May indicate data quality issue in source system

## Quality Issue Logging

All quality issues are logged to `data_quality_issues` table:

```sql
CREATE TABLE data_quality_issues (
    id SERIAL PRIMARY KEY,
    run_item_id INTEGER,
    source_name VARCHAR(100),
    issue_type VARCHAR(100),
    severity VARCHAR(50),
    row_identifier VARCHAR(255),
    issue_details TEXT,
    created_at TIMESTAMP
);
```

**Issue Types:**
- `missing_column`
- `null_value`
- `invalid_date`
- `invalid_numeric`
- `exact_duplicate`
- `business_duplicate`
- `mapping_unmatched`

**Severity Levels:**
- `error` - Fails preprocessing
- `warning` - Logged but doesn't fail

## Configuration Per Source

Quality checks are configured in `preprocessing_config.py`:

```python
SHOPIFY_CONFIG = PreprocessingConfig(
    required_columns=["day", "shipping_postal_code", "order"],
    date_columns=["day"],
    numeric_columns=["net_sales", "order_item_current_quantity", "orders"],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "order", "shipping_postal_code"],
    drop_exact_duplicates=True,
    strict_required_columns=True
)
```

## Viewing Quality Issues

### Via API

```bash
# Get all quality issues
GET /api/quality/issues?limit=100

# Get issues for specific run item
GET /api/quality/issues/run-item/{run_item_id}
```

### Via Frontend

Quality issues are displayed in the Preprocessing page:
- Issue count per source
- Issue type breakdown
- Severity indicators
- Detailed issue messages

## Best Practices

1. **Review business duplicates** - Don't ignore them, investigate root cause
2. **Monitor mapping unmatched rates** - High rates may indicate outdated mapping files
3. **Update mapping files regularly** - As new postal codes/cities appear
4. **Set appropriate business keys** - Keys should uniquely identify a business entity
5. **Use strict mode for critical sources** - Fail fast on missing required columns
6. **Log everything** - Even warnings provide valuable operational insights

## Future Enhancements

- Anomaly detection (outliers in numeric fields)
- Cross-source consistency checks
- Trend analysis of quality metrics over time
- Automated alerts for quality degradation
- Configurable quality thresholds per source
