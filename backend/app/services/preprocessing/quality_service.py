"""
Data quality checking service.
Handles duplicate detection and data validation.
"""

import pandas as pd
from typing import Dict, List, Tuple
from app.preprocessing_config import PreprocessingConfig


class QualityService:
    def check_exact_duplicates(self, df: pd.DataFrame) -> Tuple[int, pd.DataFrame]:
        """
        Check for exact duplicate rows.
        Returns: (duplicate_count, deduplicated_df)
        """
        duplicate_count = df.duplicated().sum()
        deduplicated_df = df.drop_duplicates()
        return duplicate_count, deduplicated_df

    def check_business_duplicates(
        self,
        df: pd.DataFrame,
        business_keys: List[str]
    ) -> Tuple[int, List[Dict]]:
        """
        Check for business key duplicates.
        Returns: (duplicate_count, duplicate_examples)
        """
        # Filter to only existing columns
        existing_keys = [k for k in business_keys if k in df.columns]
        if not existing_keys:
            return 0, []

        # Find duplicates based on business keys
        duplicates = df[df.duplicated(subset=existing_keys, keep=False)]
        duplicate_count = len(duplicates)

        # Get examples (first 5 duplicate groups)
        examples = []
        if duplicate_count > 0:
            duplicate_groups = duplicates.groupby(existing_keys).size().head(5)
            for keys, count in duplicate_groups.items():
                if isinstance(keys, tuple):
                    key_dict = dict(zip(existing_keys, keys))
                else:
                    key_dict = {existing_keys[0]: keys}
                examples.append({
                    "keys": key_dict,
                    "count": int(count)
                })

        return duplicate_count, examples

    def check_missing_required_columns(
        self,
        df: pd.DataFrame,
        required_columns: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if required columns are present.
        Returns: (all_present, missing_columns)
        """
        missing = [col for col in required_columns if col not in df.columns]
        return len(missing) == 0, missing

    def check_null_values(
        self,
        df: pd.DataFrame,
        columns: List[str]
    ) -> Dict[str, int]:
        """
        Check for null values in specified columns.
        Returns: dict of column -> null_count
        """
        null_counts = {}
        for col in columns:
            if col in df.columns:
                null_counts[col] = int(df[col].isna().sum())
        return null_counts

    def check_invalid_dates(
        self,
        df: pd.DataFrame,
        date_columns: List[str]
    ) -> Dict[str, int]:
        """
        Check for invalid dates.
        Returns: dict of column -> invalid_count
        """
        invalid_counts = {}
        for col in date_columns:
            if col in df.columns:
                # Try to convert to datetime and count failures
                try:
                    pd.to_datetime(df[col], errors='coerce')
                    invalid_counts[col] = int(df[col].isna().sum())
                except:
                    invalid_counts[col] = len(df)
        return invalid_counts

    def check_invalid_numerics(
        self,
        df: pd.DataFrame,
        numeric_columns: List[str]
    ) -> Dict[str, int]:
        """
        Check for invalid numeric values.
        Returns: dict of column -> invalid_count
        """
        invalid_counts = {}
        for col in numeric_columns:
            if col in df.columns:
                # Try to convert to numeric and count failures
                try:
                    pd.to_numeric(df[col], errors='coerce')
                    invalid_counts[col] = int(df[col].isna().sum())
                except:
                    invalid_counts[col] = len(df)
        return invalid_counts

    def run_quality_checks(
        self,
        df: pd.DataFrame,
        config: PreprocessingConfig
    ) -> Dict:
        """
        Run all quality checks for a source.
        Returns: dict with all quality check results
        """
        results = {
            "total_rows": len(df),
            "exact_duplicates": 0,
            "business_duplicates": 0,
            "business_duplicate_examples": [],
            "missing_columns": [],
            "null_values": {},
            "invalid_dates": {},
            "invalid_numerics": {}
        }

        # Check required columns
        all_present, missing = self.check_missing_required_columns(df, config.required_columns)
        results["missing_columns"] = missing

        if not all_present and config.strict_required_columns:
            return results  # Stop if required columns missing

        # Check exact duplicates
        if config.duplicate_exact_enabled:
            dup_count, _ = self.check_exact_duplicates(df)
            results["exact_duplicates"] = dup_count

        # Check business duplicates
        if config.duplicate_business_keys:
            dup_count, examples = self.check_business_duplicates(df, config.duplicate_business_keys)
            results["business_duplicates"] = dup_count
            results["business_duplicate_examples"] = examples

        # Check null values in required columns
        null_counts = self.check_null_values(df, config.required_columns)
        results["null_values"] = null_counts

        # Check invalid dates
        invalid_dates = self.check_invalid_dates(df, config.date_columns)
        results["invalid_dates"] = invalid_dates

        # Check invalid numerics
        invalid_numerics = self.check_invalid_numerics(df, config.numeric_columns)
        results["invalid_numerics"] = invalid_numerics

        return results
