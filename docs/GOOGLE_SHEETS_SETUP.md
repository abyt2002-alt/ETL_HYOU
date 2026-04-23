# Google Sheets Setup Guide

This guide explains how to set up Google Sheets and service account credentials for the ingestion platform.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Data Ingestion Platform"
4. Click "Create"

## Step 2: Enable Google Sheets API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and click "Enable"

## Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Enter details:
   - Service account name: `ingestion-service`
   - Service account ID: `ingestion-service` (auto-filled)
   - Description: "Service account for data ingestion"
4. Click "Create and Continue"
5. Skip optional steps (roles and user access)
6. Click "Done"

## Step 4: Create Service Account Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" → "Create new key"
5. Select "JSON" format
6. Click "Create"
7. The JSON key file will download automatically
8. Rename it to `credentials.json`
9. Move it to `backend/credentials.json` in your project

## Step 5: Prepare Your Google Sheet

### Create Sheet Structure

Your Google Sheet should have separate tabs for each data source:

**Tab: Meta**
| Day | DMA region | Impressions | Amount spent |
|-----|------------|-------------|--------------|
| 44927 | New York | 1500 | 250.50 |
| 44928 | Los Angeles | 2000 | 300.75 |

**Tab: Shopify**
| Day | Shipping postal code | Order | Customer type | Net sales | Order item current quantity | Orders |
|-----|---------------------|-------|---------------|-----------|----------------------------|--------|
| 44927 | 10001 | #1001 | Returning | 150.00 | 2 | 1 |

**Tab: GA**
| Day | Region | Session source | City | Sessions |
|-----|--------|----------------|------|----------|
| 44927 | New York | google | New York | 500 |

**Tab: GAds**
| Campaign | Day | Cost | Impr |
|----------|-----|------|------|
| Summer Sale | 44927 | 100.50 | 5000 |

### Important Notes

1. **Tab Names**: Must match exactly (case-sensitive):
   - `Meta`
   - `Shopify`
   - `GA`
   - `GAds`

2. **Column Names**: Must match exactly (case-sensitive, including spaces):
   - "Day" not "Date"
   - "DMA region" not "DMA Region" or "DMA_region"
   - "Amount spent" not "Amount Spent"

3. **Date Format**: 
   - Excel serial numbers (e.g., 44927) work best
   - String dates also work: "2024-01-15", "01/15/2024"
   - Ensure consistent format within each column

4. **Header Row**: First row must contain column names

5. **No Empty Rows**: Don't leave empty rows between data

## Step 6: Share Sheet with Service Account

1. Open your Google Sheet
2. Click "Share" button (top right)
3. Enter the service account email:
   - Found in `credentials.json` as `client_email`
   - Format: `ingestion-service@project-id.iam.gserviceaccount.com`
4. Set permission to "Viewer" (read-only is sufficient)
5. Uncheck "Notify people"
6. Click "Share"

## Step 7: Get Sheet ID

The Sheet ID is in the URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
                                        ^^^^^^^^^^^^^^^^
```

Copy this ID and add it to your `.env` file:
```env
GOOGLE_SHEET_ID=your_sheet_id_here
```

## Example credentials.json Structure

Your `credentials.json` should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "ingestion-service@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## Testing the Connection

After setup, test the connection:

1. Start the platform:
```bash
docker-compose up -d
```

2. Check backend logs:
```bash
docker-compose logs backend
```

3. Try listing sources:
```bash
curl http://localhost:8000/api/sources
```

4. Try a test ingestion:
```bash
curl -X POST http://localhost:8000/api/ingest/meta \
  -H "Content-Type: application/json" \
  -d '{"triggered_by": "test"}'
```

## Common Issues

### "Permission denied" error

**Cause**: Sheet not shared with service account

**Fix**: 
1. Check service account email in `credentials.json`
2. Verify sheet is shared with that email
3. Ensure permission is at least "Viewer"

### "Worksheet not found" error

**Cause**: Tab name doesn't match configuration

**Fix**:
1. Check exact tab names in your sheet
2. Compare with `sheet_tab_name` in `backend/app/source_config.py`
3. Names are case-sensitive

### "Invalid credentials" error

**Cause**: Credentials file is invalid or not found

**Fix**:
1. Verify `credentials.json` exists at `backend/credentials.json`
2. Check JSON is valid (no syntax errors)
3. Ensure file was downloaded correctly from Google Cloud

### "API not enabled" error

**Cause**: Google Sheets API not enabled

**Fix**:
1. Go to Google Cloud Console
2. Enable Google Sheets API
3. Wait a few minutes for propagation

## Date Format Examples

The platform handles multiple date formats:

**Excel Serial Numbers** (Recommended):
```
44927  → 2023-01-15
44928  → 2023-01-16
```

**ISO Format**:
```
2023-01-15
2023-01-16
```

**US Format**:
```
01/15/2023
01/16/2023
```

**European Format**:
```
15/01/2023
16/01/2023
```

## Security Best Practices

1. **Never commit credentials.json**:
   - Already in `.gitignore`
   - Don't share publicly

2. **Limit service account permissions**:
   - Only grant "Viewer" access to sheets
   - Don't give broader project permissions

3. **Rotate credentials regularly**:
   - Create new key every 90 days
   - Delete old keys

4. **Use separate accounts per environment**:
   - Different service account for dev/staging/prod
   - Easier to track and revoke

5. **Monitor usage**:
   - Check Google Cloud Console for API usage
   - Set up alerts for unusual activity

## Adding More Tabs

When you add a new tab to your sheet:

1. Create the tab with proper column names
2. Add data following the format
3. Update `backend/app/source_config.py` with new source
4. Create database model
5. Run migration
6. Restart backend

See [ADDING_SOURCES.md](ADDING_SOURCES.md) for detailed instructions.

## Sample Data

For testing, you can use this sample data:

**Meta Tab**:
```
Day,DMA region,Impressions,Amount spent
44927,New York,1500,250.50
44928,Los Angeles,2000,300.75
44929,Chicago,1800,275.25
```

**Shopify Tab**:
```
Day,Shipping postal code,Order,Customer type,Net sales,Order item current quantity,Orders
44927,10001,#1001,Returning,150.00,2,1
44928,90001,#1002,New,200.00,3,1
44929,60601,#1003,Returning,175.50,1,1
```

Copy and paste into your Google Sheet, ensuring the first row contains headers.
