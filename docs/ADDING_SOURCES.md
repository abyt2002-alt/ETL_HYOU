# Adding New Sources - Step by Step Guide

This guide walks through adding a new data source to the ingestion platform.

## Example: Adding a "TikTok" Source

Let's say you have a new Google Sheet tab called "TikTok" with these columns:
- Date (date)
- Campaign Name (string)
- Video Views (integer)
- Spend (numeric)

## Step 1: Define Source Configuration

Edit `backend/app/source_config.py` and add to the `SOURCES` list:

```python
SourceConfig(
    source_name="tiktok",
    sheet_tab_name="TikTok",
    target_table_name="raw_tiktok",
    required_columns=["Date", "Campaign Name", "Video Views", "Spend"],
    optional_columns=[],
    field_types={
        "Date": "date",
        "Campaign Name": "string",
        "Video Views": "integer",
        "Spend": "numeric"
    },
    date_fields=["Date"],
    numeric_fields=["Spend"],
    load_mode="append"
)
```

### Configuration Fields Explained

- `source_name`: Internal identifier (lowercase, no spaces)
- `sheet_tab_name`: Exact name of the Google Sheet tab
- `target_table_name`: PostgreSQL table name (prefix with `raw_`)
- `required_columns`: Columns that must exist in the sheet
- `optional_columns`: Columns that may or may not exist
- `field_types`: Type mapping for each column
- `date_fields`: Columns containing dates (for Excel conversion)
- `numeric_fields`: Columns with decimal numbers
- `load_mode`: How to load data (`append` is standard)

## Step 2: Create Database Model

Edit `backend/app/models.py` and add:

```python
class RawTiktok(Base):
    __tablename__ = "raw_tiktok"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    campaign_name = Column(String(255))
    video_views = Column(Integer)
    spend = Column(Numeric(10, 2))
    ingested_at = Column(DateTime, default=datetime.utcnow)
```

### Model Guidelines

- Class name: PascalCase version of table name
- Table name: Match `target_table_name` from config
- Column names: Lowercase with underscores (normalized from sheet columns)
- Always include `id` and `ingested_at`
- Use appropriate SQLAlchemy types:
  - `String(length)` for text
  - `Integer` for whole numbers
  - `Numeric(precision, scale)` for decimals
  - `Date` for dates
  - `DateTime` for timestamps

## Step 3: Generate Migration

From the `backend` directory:

```bash
alembic revision --autogenerate -m "add tiktok source"
```

This creates a new migration file in `backend/alembic/versions/`.

Review the generated migration to ensure it looks correct.

## Step 4: Apply Migration

```bash
alembic upgrade head
```

This creates the `raw_tiktok` table in PostgreSQL.

## Step 5: Test

1. Restart the backend (if running):
   ```bash
   docker-compose restart backend
   ```

2. Open the frontend at http://localhost:5173

3. Navigate to "Sources" - you should see "tiktok" listed

4. Click "Run" to test ingestion

5. Check "Runs" page for results

6. Click "Preview" to view loaded data

## That's It!

The ingestion engine automatically:
- Reads from the TikTok sheet tab
- Validates columns
- Converts Excel dates
- Coerces types
- Loads into `raw_tiktok` table
- Tracks success/failure

## Common Issues

### Issue: "Missing required columns"

**Cause**: Sheet column names don't match `required_columns`

**Fix**: Ensure exact match (case-sensitive, including spaces)

### Issue: "Unexpected columns found"

**Cause**: Sheet has extra columns not in config

**Fix**: Add them to `optional_columns` or remove from sheet

### Issue: "Cannot convert date"

**Cause**: Date format not recognized

**Fix**: Ensure dates are Excel serial numbers or standard formats (YYYY-MM-DD, MM/DD/YYYY)

### Issue: Migration fails

**Cause**: Model doesn't match existing schema

**Fix**: Review migration file, adjust model, regenerate migration

## Advanced: Optional Columns

If some columns may not always be present:

```python
SourceConfig(
    source_name="tiktok",
    required_columns=["Date", "Campaign Name", "Video Views"],
    optional_columns=["Spend", "Engagement Rate"],
    # ...
)
```

The ingestion will succeed even if optional columns are missing.

## Advanced: Custom Transformations

If you need source-specific transformation logic:

1. Edit `backend/app/services/transform_service.py`
2. Add a method for your source
3. Call it from `transform_data()` based on source name

Example:

```python
def transform_data(self, data: List[Dict[str, Any]], config: SourceConfig) -> pd.DataFrame:
    df = pd.DataFrame(data)
    
    # Standard transformations
    for date_field in config.date_fields:
        df[date_field] = df[date_field].apply(self.convert_excel_date)
    
    # Source-specific transformation
    if config.source_name == "tiktok":
        df = self._transform_tiktok(df)
    
    # Continue with standard logic...
    return df

def _transform_tiktok(self, df: pd.DataFrame) -> pd.DataFrame:
    # Custom logic for TikTok data
    df['campaign_name'] = df['campaign_name'].str.upper()
    return df
```

However, prefer config-driven behavior over source-specific code when possible.
