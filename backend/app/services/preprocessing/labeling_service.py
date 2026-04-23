"""
Source labeling service for GA session sources.
"""

import pandas as pd
from typing import Dict, List


class LabelingService:
    def apply_source_labels(
        self,
        df: pd.DataFrame,
        session_source_column: str,
        label_rules: Dict[str, List[str]]
    ) -> pd.DataFrame:
        """
        Apply source labels to GA data based on session source.
        
        Args:
            df: DataFrame with session source data
            session_source_column: Name of the session source column
            label_rules: Dict mapping label names to list of keywords
        
        Returns:
            DataFrame with source_label column added
        """
        if session_source_column not in df.columns:
            df['source_label'] = 'Unlabeled'
            return df

        # Create source_label column
        df['source_label'] = 'Unlabeled'

        # Apply rules in order
        for label, keywords in label_rules.items():
            # Create mask for rows matching any keyword
            mask = df[session_source_column].str.lower().str.contains(
                '|'.join(keywords),
                case=False,
                na=False,
                regex=True
            )
            df.loc[mask, 'source_label'] = label

        return df

    def get_label_distribution(
        self,
        df: pd.DataFrame,
        label_column: str = 'source_label'
    ) -> Dict[str, int]:
        """
        Get distribution of source labels.
        
        Returns:
            Dict mapping label -> count
        """
        if label_column not in df.columns:
            return {}

        distribution = df[label_column].value_counts().to_dict()
        return {str(k): int(v) for k, v in distribution.items()}
