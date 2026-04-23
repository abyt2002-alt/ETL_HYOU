# API Specification

Base URL: `http://localhost:8000/api`

## Endpoints

### Health Check

**GET** `/health`

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "service": "ingestion-platform"
}
```

---

### List Sources

**GET** `/sources`

Get all configured data sources.

**Response**:
```json
[
  {
    "source_name": "meta",
    "sheet_tab_name": "Meta",
    "target_table_name": "raw_meta",
    "required_columns": ["Day", "DMA region", "Impressions", "Amount spent"],
    "optional_columns": [],
    "field_types": {
      "Day": "date",
      "DMA region": "string",
      "Impressions": "integer",
      "Amount spent": "numeric"
    },
    "date_fields": ["Day"],
    "numeric_fields": ["Amount spent"],
    "load_mode": "append"
  }
]
```

---

### Run All Sources

**POST** `/ingest/all`

Trigger ingestion for all configured sources.

**Request Body**:
```json
{
  "triggered_by": "user"
}
```

**Response**:
```json
{
  "id": 1,
  "trigger_type": "all_sources",
  "status": "running",
  "started_at": "2024-01-15T10:30:00",
  "completed_at": null,
  "triggered_by": "user",
  "summary_message": null
}
```

---

### Run Single Source

**POST** `/ingest/{source_name}`

Trigger ingestion for a specific source.

**Path Parameters**:
- `source_name` (string): Name of the source to ingest

**Request Body**:
```json
{
  "triggered_by": "user"
}
```

**Response**:
```json
{
  "id": 2,
  "trigger_type": "single_source",
  "status": "running",
  "started_at": "2024-01-15T10:35:00",
  "completed_at": null,
  "triggered_by": "user",
  "summary_message": null
}
```

**Error Response** (404):
```json
{
  "detail": "Source 'invalid_source' not found"
}
```

---

### Get Latest Run

**GET** `/runs/latest`

Get the most recent ingestion run with details.

**Response**:
```json
{
  "run": {
    "id": 1,
    "trigger_type": "all_sources",
    "status": "completed",
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:32:15",
    "triggered_by": "user",
    "summary_message": "Completed: 4 succeeded, 0 failed"
  },
  "items": [
    {
      "id": 1,
      "run_id": 1,
      "source_name": "meta",
      "sheet_tab_name": "Meta",
      "target_table_name": "raw_meta",
      "status": "completed",
      "rows_read": 150,
      "rows_loaded": 150,
      "rows_failed": 0,
      "started_at": "2024-01-15T10:30:05",
      "completed_at": "2024-01-15T10:30:45",
      "error_message": null
    }
  ]
}
```

---

### Get Run History

**GET** `/runs`

Get list of all ingestion runs.

**Query Parameters**:
- `limit` (integer, optional): Maximum number of runs to return (default: 50)

**Response**:
```json
[
  {
    "id": 2,
    "trigger_type": "single_source",
    "status": "completed",
    "started_at": "2024-01-15T10:35:00",
    "completed_at": "2024-01-15T10:35:30",
    "triggered_by": "user",
    "summary_message": "Successfully ingested meta"
  },
  {
    "id": 1,
    "trigger_type": "all_sources",
    "status": "completed",
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:32:15",
    "triggered_by": "user",
    "summary_message": "Completed: 4 succeeded, 0 failed"
  }
]
```

---

### Get Run Detail

**GET** `/runs/{run_id}`

Get detailed information about a specific run.

**Path Parameters**:
- `run_id` (integer): ID of the run

**Response**:
```json
{
  "run": {
    "id": 1,
    "trigger_type": "all_sources",
    "status": "partial",
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:32:15",
    "triggered_by": "user",
    "summary_message": "Completed: 3 succeeded, 1 failed"
  },
  "items": [
    {
      "id": 1,
      "run_id": 1,
      "source_name": "meta",
      "sheet_tab_name": "Meta",
      "target_table_name": "raw_meta",
      "status": "completed",
      "rows_read": 150,
      "rows_loaded": 150,
      "rows_failed": 0,
      "started_at": "2024-01-15T10:30:05",
      "completed_at": "2024-01-15T10:30:45",
      "error_message": null
    },
    {
      "id": 2,
      "run_id": 1,
      "source_name": "shopify",
      "sheet_tab_name": "Shopify",
      "target_table_name": "raw_shopify",
      "status": "failed",
      "rows_read": 0,
      "rows_loaded": 0,
      "rows_failed": 0,
      "started_at": "2024-01-15T10:30:46",
      "completed_at": "2024-01-15T10:30:50",
      "error_message": "Missing required columns: {'Order'}"
    }
  ]
}
```

**Error Response** (404):
```json
{
  "detail": "Run not found"
}
```

---

### Preview Data

**GET** `/data/{table_name}`

Preview data from a specific table.

**Path Parameters**:
- `table_name` (string): Name of the table

**Query Parameters**:
- `limit` (integer, optional): Maximum number of rows (default: 100)

**Response**:
```json
{
  "table_name": "raw_meta",
  "rows": [
    {
      "id": 1,
      "day": "2024-01-15",
      "dma_region": "New York",
      "impressions": 1500,
      "amount_spent": "250.50",
      "ingested_at": "2024-01-15T10:30:45"
    }
  ],
  "count": 1
}
```

**Error Response** (400):
```json
{
  "detail": "Table does not exist"
}
```

---

## Status Values

### Run Status
- `running`: Ingestion in progress
- `completed`: All sources succeeded
- `partial`: Some sources failed
- `failed`: Run failed completely

### Item Status
- `running`: Source ingestion in progress
- `completed`: Source ingested successfully
- `failed`: Source ingestion failed

## Error Handling

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

Error responses include a `detail` field with a descriptive message.
