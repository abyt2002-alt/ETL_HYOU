"""
Main preprocessing orchestration service.
Coordinates preprocessing operations for all sources.
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict
from datetime import date, datetime

from app.preprocessing_config import get_preprocessing_config, list_preprocessing_sources
from app.repositories.preprocessing_repository import PreprocessingRepository
from app.services.preprocessing.mapping_service import MappingService
from app.services.preprocessing.quality_service import QualityService
from app.services.preprocessing.labeling_service import LabelingService
from app.services.preprocessing.curated_writer_service import CuratedWriterService


class PreprocessingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PreprocessingRepository(db)
        self.mapping_service = MappingService(db)
        self.quality_service = QualityService()
        self.labeling_service = LabelingService()
        self.writer_service = CuratedWriterService(db)

    def run_all_sources(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        triggered_by: str = "system"
    ):
        """Run preprocessing for all sources."""
        run = self.repo.create_run(triggered_by=triggered_by)
        
        sources = list_preprocessing_sources()
        completed_count = 0
        failed_count = 0

        for source_name in sources:
            try:
                self.run_single_source(
                    source_name=source_name,
                    start_date=start_date,
                    end_date=end_date,
                    run_id=run.id
                )
                completed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Error preprocessing {source_name}: {e}")

        # Complete the run
        if failed_count == 0:
            status = "completed"
            summary = f"All {completed_count} sources preprocessed successfully"
        elif completed_count == 0:
            status = "failed"
            summary = f"All {failed_count} sources failed"
        else:
            status = "partial"
            summary = f"{completed_count} sources completed, {failed_count} failed"

        self.repo.complete_run(run.id, status, summary)
        return run

    def run_single_source(
        self,
        source_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        triggered_by: str = "system",
        run_id: Optional[int] = None
    ):
        """Run preprocessing for a single source."""
        # Get config
        config = get_preprocessing_config(source_name)

        # Create run if not provided
        if run_id is None:
            run = self.repo.create_run(triggered_by=triggered_by)
            run_id = run.id

        # Get active mapping file if required
        mapping_file_id = None
        if config.mapping_required:
            mapping_file = self.mapping_service.get_active_mapping_file_info(config.mapping_type)
            if mapping_file:
                mapping_file_id = mapping_file.id

        # Create run item
        run_item = self.repo.create_run_item(
            run_id=run_id,
            source_name=source_name,
            input_table=config.raw_table_name,
            output_table=config.curated_table_name,
            mapping_file_id=mapping_file_id
        )

        try:
            # Load raw data
            df = self._load_raw_data(config.raw_table_name, start_date, end_date)
            rows_read = len(df)

            if df.empty:
                self.repo.update_run_item(
                    run_item.id,
                    status="completed",
                    rows_read=0,
                    rows_output=0
                )
                return run_item

            # Run quality checks
            quality_results = self.quality_service.run_quality_checks(df, config)

            # Check for fatal issues
            if quality_results["missing_columns"] and config.strict_required_columns:
                error_msg = f"Missing required columns: {', '.join(quality_results['missing_columns'])}"
                self.repo.update_run_item(
                    run_item.id,
                    status="failed",
                    rows_read=rows_read,
                    error_message=error_msg
                )
                self._log_quality_issues(run_item.id, source_name, quality_results)
                return run_item

            # Remove exact duplicates if configured
            exact_dup_count = quality_results["exact_duplicates"]
            if config.drop_exact_duplicates and exact_dup_count > 0:
                _, df = self.quality_service.check_exact_duplicates(df)

            # Apply source-specific preprocessing
            df, mapping_stats, unlabeled_count = self._preprocess_source(df, config)

            # Write to curated table
            rows_output = self.writer_service.write_curated_data(
                df,
                config.curated_table_name,
                truncate_first=True
            )

            # Update run item with results
            self.repo.update_run_item(
                run_item.id,
                status="completed",
                rows_read=rows_read,
                rows_output=rows_output,
                exact_duplicates_found=exact_dup_count,
                business_duplicates_found=quality_results["business_duplicates"],
                mapping_matches=mapping_stats.get("matched", 0),
                mapping_unmatched=mapping_stats.get("unmatched", 0),
                unlabeled_count=unlabeled_count,
                issues_found=self._count_issues(quality_results)
            )

            # Log quality issues
            self._log_quality_issues(run_item.id, source_name, quality_results)

            return run_item

        except Exception as e:
            self.repo.update_run_item(
                run_item.id,
                status="failed",
                error_message=str(e)
            )
            raise

    def _load_raw_data(
        self,
        table_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Load raw data from database."""
        query = f"SELECT * FROM {table_name}"
        params = {}
        
        conditions = []
        if start_date:
            conditions.append("day >= :start_date")
            params["start_date"] = start_date
        if end_date:
            conditions.append("day <= :end_date")
            params["end_date"] = end_date
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql(text(query), self.db.bind, params=params)
        return df

    def _preprocess_source(self, df: pd.DataFrame, config) -> tuple:
        """Apply source-specific preprocessing logic."""
        mapping_stats = {"matched": 0, "unmatched": 0}
        unlabeled_count = 0

        if config.source_name == "shopify":
            df, mapping_stats = self._preprocess_shopify(df)
        elif config.source_name == "ga":
            df, mapping_stats, unlabeled_count = self._preprocess_ga(df, config)
        elif config.source_name == "gads":
            df = self._preprocess_gads(df)
        elif config.source_name == "meta":
            df = self._preprocess_meta(df)

        return df, mapping_stats, unlabeled_count

    def _preprocess_shopify(self, df: pd.DataFrame) -> tuple:
        """Preprocess Shopify data with DMA enrichment."""
        mapping_stats = {"matched": 0, "unmatched": 0}

        # Clean postal code
        df['shipping_postal_code_cleaned'] = df['shipping_postal_code'].astype(str).str.strip()
        df['shipping_postal_code_cleaned'] = df['shipping_postal_code_cleaned'].str.split('-').str[0]

        # Load mapping file
        mapping_df = self.mapping_service.load_mapping_file("shopify_dma")
        
        if mapping_df is not None:
            # Clean mapping zip code
            mapping_df['Zip Code'] = mapping_df['Zip Code'].astype(str).str.strip()
            mapping_df['Zip Code'] = mapping_df['Zip Code'].str.split('-').str[0]
            
            # Deduplicate mapping on zip
            mapping_df = mapping_df.drop_duplicates(subset=['Zip Code'], keep='first')
            
            # Merge
            df = df.merge(
                mapping_df[['Zip Code', 'DMA Description']],
                left_on='shipping_postal_code_cleaned',
                right_on='Zip Code',
                how='left'
            )
            
            df['dma'] = df['DMA Description']
            df = df.drop(columns=['Zip Code', 'DMA Description'], errors='ignore')
            
            # Calculate stats
            mapping_stats["matched"] = int(df['dma'].notna().sum())
            mapping_stats["unmatched"] = int(df['dma'].isna().sum())
        else:
            df['dma'] = None

        return df, mapping_stats

    def _preprocess_ga(self, df: pd.DataFrame, config) -> tuple:
        """Preprocess GA data with DMA enrichment and source labeling."""
        mapping_stats = {"matched": 0, "unmatched": 0}

        # Normalize city and region
        df['city_normalized'] = df['city'].astype(str).str.lower().str.strip()
        df['region_normalized'] = df['region'].astype(str).str.lower().str.strip()

        # Load mapping file
        mapping_df = self.mapping_service.load_mapping_file("ga_dma")
        
        if mapping_df is not None:
            # Normalize mapping
            mapping_df['City'] = mapping_df['City'].astype(str).str.lower().str.strip()
            mapping_df['Region'] = mapping_df['Region'].astype(str).str.lower().str.strip()
            
            # Deduplicate mapping
            mapping_df = mapping_df.drop_duplicates(subset=['City', 'Region'], keep='first')
            
            # Merge
            df = df.merge(
                mapping_df[['City', 'Region', 'DMA']],
                left_on=['city_normalized', 'region_normalized'],
                right_on=['City', 'Region'],
                how='left'
            )
            
            df['dma'] = df['DMA']
            df = df.drop(columns=['City', 'Region', 'DMA', 'city_normalized', 'region_normalized'], errors='ignore')
            
            # Calculate stats
            mapping_stats["matched"] = int(df['dma'].notna().sum())
            mapping_stats["unmatched"] = int(df['dma'].isna().sum())
        else:
            df['dma'] = None
            df = df.drop(columns=['city_normalized', 'region_normalized'], errors='ignore')

        # Apply source labels
        if config.source_label_rules:
            df = self.labeling_service.apply_source_labels(
                df,
                'session_source',
                config.source_label_rules
            )
            unlabeled_count = int((df['source_label'] == 'Unlabeled').sum())
        else:
            df['source_label'] = 'Unlabeled'
            unlabeled_count = len(df)

        return df, mapping_stats, unlabeled_count

    def _preprocess_gads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess GAds data."""
        # Rename impr_ to impr for curated table
        if 'impr_' in df.columns:
            df['impr'] = df['impr_']
            df = df.drop(columns=['impr_'], errors='ignore')
        
        # Drop ingested_at and id if present
        df = df.drop(columns=['id', 'ingested_at'], errors='ignore')
        
        return df

    def _preprocess_meta(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess Meta data."""
        # Drop ingested_at and id if present
        df = df.drop(columns=['id', 'ingested_at'], errors='ignore')
        return df

    def _count_issues(self, quality_results: Dict) -> int:
        """Count total issues from quality results."""
        count = 0
        count += len(quality_results.get("missing_columns", []))
        count += sum(quality_results.get("null_values", {}).values())
        count += sum(quality_results.get("invalid_dates", {}).values())
        count += sum(quality_results.get("invalid_numerics", {}).values())
        return count

    def _log_quality_issues(self, run_item_id: int, source_name: str, quality_results: Dict):
        """Log quality issues to database."""
        # Log missing columns
        for col in quality_results.get("missing_columns", []):
            self.repo.log_quality_issue(
                run_item_id=run_item_id,
                source_name=source_name,
                issue_type="missing_column",
                severity="error",
                issue_details=f"Required column '{col}' is missing"
            )

        # Log business duplicates
        if quality_results.get("business_duplicates", 0) > 0:
            examples = quality_results.get("business_duplicate_examples", [])
            self.repo.log_quality_issue(
                run_item_id=run_item_id,
                source_name=source_name,
                issue_type="business_duplicate",
                severity="warning",
                issue_details=f"Found {quality_results['business_duplicates']} business duplicates. Examples: {examples[:3]}"
            )
