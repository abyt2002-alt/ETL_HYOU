# Preprocessing Layer - Ready for Use

## Status: ✅ Complete and Deployed

The preprocessing layer has been successfully implemented and is running on the `preprocessing` branch.

## What's Working

### Backend Services
✅ Preprocessing API endpoints operational  
✅ Mapping file management system ready  
✅ Quality checking service active  
✅ Curated data writing functional  
✅ All 4 sources configured (Shopify, GA, GAds, Meta)  

### Frontend
✅ Preprocessing page accessible at http://localhost:3000/preprocessing  
✅ Source cards displaying  
✅ Run buttons functional  
✅ Statistics display working  

### Database
✅ All preprocessing tables created  
✅ All curated tables created  
✅ Migration 004 applied successfully  

## Quick Start

### 1. Access the Preprocessing Page
Navigate to: http://localhost:3000/preprocessing

### 2. Run Preprocessing
- Click "Run All Sources" to process all sources
- Or click "Run" on individual source cards

### 3. View Results
Each source card shows:
- Rows read and output
- Exact duplicates found
- Business duplicates found
- Mapping matches/unmatched (Shopify, GA)
- Unlabeled count (GA only)
- Issues found
- Error messages (if any)

## API Testing

### List Sources
```bash
curl http://localhost:8000/api/preprocessing/sources
```

### Run All Sources
```bash
curl -X POST http://localhost:8000/api/preprocessing/run/all \
  -H "Content-Type: application/json" \
  -d '{"triggered_by": "user"}'
```

### Run Single Source
```bash
curl -X POST http://localhost:8000/api/preprocessing/run/shopify \
  -H "Content-Type: application/json" \
  -d '{"triggered_by": "user"}'
```

### Get Latest Run
```bash
curl http://localhost:8000/api/preprocessing/runs/latest
```

### Preview Curated Data
```bash
curl http://localhost:8000/api/preprocessing/curated/curated_shopify?limit=10
```

## Current Branch Structure

### ingestion branch
- Layer 1: Data ingestion
- Excel → Raw PostgreSQL tables
- 4 sources: Meta, Shopify, GA, GAds

### preprocessing branch (current)
- Layer 2: Data preprocessing
- Raw tables → Curated tables
- DMA enrichment, source labeling, quality checks

## Next Steps

### 1. Upload Mapping Files (Optional)
If you have actual mapping files, upload them via API:

```bash
# Upload Shopify DMA mapping
curl -X POST http://localhost:8000/api/mapping-files/upload \
  -F "file=@your_pincode_mapping.csv" \
  -F "mapping_name=Shopify DMA Mapping" \
  -F "source_name=shopify" \
  -F "mapping_type=shopify_dma" \
  -F "required_columns=[\"Zip Code\",\"DMA Description\"]" \
  -F "uploaded_by=admin"

# Activate the uploaded file
curl -X POST http://localhost:8000/api/mapping-files/{id}/activate?mapping_type=shopify_dma
```

### 2. Test with Real Data
- Ensure ingestion has run successfully
- Run preprocessing on all sources
- Check curated tables for enriched data
- Review quality issues

### 3. Monitor Quality
- Check mapping match rates
- Review business duplicates
- Monitor unlabeled GA sources
- Adjust configurations as needed

## Configuration

### Preprocessing Config Location
`backend/app/preprocessing_config.py`

### Modify Source Behavior
Edit the config for any source:
```python
SHOPIFY_CONFIG = PreprocessingConfig(
    source_name="shopify",
    required_columns=["day", "shipping_postal_code", "order"],
    duplicate_business_keys=["day", "order", "shipping_postal_code"],
    mapping_required=True,
    drop_exact_duplicates=True,
    # ... other settings
)
```

### GA Source Labels
Modify label rules in `GA_CONFIG`:
```python
source_label_rules={
    "Meta": ["facebook", "fb", "instagram", "ig", "meta"],
    "Google": ["google", "gclid", "adwords", "ads", "youtube", "yt"]
}
```

## Troubleshooting

### Preprocessing Fails
1. Check backend logs: `docker-compose logs backend`
2. Verify raw tables have data
3. Check quality issues: `GET /api/quality/issues`

### Low Mapping Match Rate
1. Check if mapping file is activated
2. Preview mapping file to verify format
3. Review data cleaning logic in docs

### Frontend Not Showing Data
1. Verify backend is running: `docker-compose ps`
2. Check API endpoint: `curl http://localhost:8000/api/preprocessing/sources`
3. Check browser console for errors

## Documentation

- **PREPROCESSING_FLOW.md** - Complete architecture and flow
- **DATA_QUALITY_RULES.md** - Quality checks explained
- **MAPPING_FILES.md** - Mapping file management
- **PREPROCESSING_SUMMARY.md** - Implementation details

## Git Commands

### Current Branch
```bash
git branch
# * preprocessing
```

### Switch Branches
```bash
# Switch to ingestion
git checkout ingestion

# Switch back to preprocessing
git checkout preprocessing
```

### Pull Latest Changes
```bash
git pull origin preprocessing
```

## Services Status

All services should be running:
```bash
docker-compose ps
```

Expected output:
- ✅ hyou_pipeline-backend-1 (running)
- ✅ hyou_pipeline-frontend-1 (running)
- ✅ hyou_pipeline-db-1 (running)

## Key Features

1. **Config-Driven** - Easy to add new sources
2. **External Mapping Files** - Upload and manage separately
3. **Quality Checks** - Comprehensive validation
4. **Duplicate Detection** - Exact and business duplicates
5. **Curated Persistence** - Processed data stored in PostgreSQL
6. **Operational Tracking** - Every run logged
7. **Source Labeling** - GA session sources categorized
8. **DMA Enrichment** - Shopify and GA enriched with DMA

## Production Readiness

**Current Status:** Production-structured foundation

**Implemented:**
- Core preprocessing logic
- Quality checks
- Run tracking
- API endpoints
- Frontend UI

**Not Yet Implemented:**
- Authentication/authorization
- Automated scheduling
- Comprehensive tests
- Monitoring/alerting
- Incremental processing

## Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review API at http://localhost:8000/docs
3. Check backend logs for errors
4. Verify database tables exist

---

**Repository:** https://github.com/abyt2002-alt/ETL_HYOU.git  
**Branch:** preprocessing  
**Status:** ✅ Ready for use
