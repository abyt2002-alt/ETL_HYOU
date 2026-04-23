"""
Preprocessing configuration for each source.
Defines rules, mappings, and quality checks per source.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PreprocessingConfig:
    source_name: str
    raw_table_name: str
    curated_table_name: str
    required_columns: List[str]
    optional_columns: List[str]
    date_columns: List[str]
    numeric_columns: List[str]
    duplicate_exact_enabled: bool
    duplicate_business_keys: List[str]
    mapping_required: bool
    mapping_type: Optional[str]
    drop_exact_duplicates: bool
    strict_required_columns: bool
    output_columns: List[str]
    source_label_rules: Optional[Dict[str, List[str]]] = None


# Shopify preprocessing configuration
SHOPIFY_CONFIG = PreprocessingConfig(
    source_name="shopify",
    raw_table_name="raw_shopify",
    curated_table_name="curated_shopify",
    required_columns=["day", "shipping_postal_code", "order"],
    optional_columns=["customer_type", "net_sales", "order_item_current_quantity", "orders"],
    date_columns=["day"],
    numeric_columns=["net_sales", "order_item_current_quantity", "orders"],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "order", "shipping_postal_code"],
    mapping_required=True,
    mapping_type="shopify_dma",
    drop_exact_duplicates=True,
    strict_required_columns=True,
    output_columns=[
        "day", "shipping_postal_code", "shipping_postal_code_cleaned",
        "order", "customer_type", "net_sales", "order_item_current_quantity",
        "orders", "dma"
    ]
)

# Google Analytics preprocessing configuration
GA_CONFIG = PreprocessingConfig(
    source_name="ga",
    raw_table_name="raw_ga",
    curated_table_name="curated_ga",
    required_columns=["day", "city", "region", "session_source"],
    optional_columns=["sessions"],
    date_columns=["day"],
    numeric_columns=["sessions"],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "city", "region", "session_source"],
    mapping_required=True,
    mapping_type="ga_dma",
    drop_exact_duplicates=True,
    strict_required_columns=True,
    output_columns=["day", "region", "session_source", "city", "sessions", "dma", "source_label"],
    source_label_rules={
        "Meta": [
            "facebook", "fb", "instagram", "ig", "meta"
        ],
        "Google": [
            "google", "gclid", "adwords", "ads", "youtube", "yt"
        ]
    }
)

# Google Ads preprocessing configuration
GADS_CONFIG = PreprocessingConfig(
    source_name="gads",
    raw_table_name="raw_gads",
    curated_table_name="curated_gads",
    required_columns=["day", "campaign"],
    optional_columns=["cost", "impr_"],
    date_columns=["day"],
    numeric_columns=["cost", "impr_"],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "campaign"],
    mapping_required=False,
    mapping_type=None,
    drop_exact_duplicates=True,
    strict_required_columns=True,
    output_columns=["campaign", "day", "cost", "impr"]
)

# Meta preprocessing configuration
META_CONFIG = PreprocessingConfig(
    source_name="meta",
    raw_table_name="raw_meta",
    curated_table_name="curated_meta",
    required_columns=["day", "dma_region"],
    optional_columns=["impressions", "amount_spent"],
    date_columns=["day"],
    numeric_columns=["impressions", "amount_spent"],
    duplicate_exact_enabled=True,
    duplicate_business_keys=["day", "dma_region"],
    mapping_required=False,
    mapping_type=None,
    drop_exact_duplicates=True,
    strict_required_columns=True,
    output_columns=["day", "dma_region", "impressions", "amount_spent"]
)


# Registry of all preprocessing configs
PREPROCESSING_CONFIGS = {
    "shopify": SHOPIFY_CONFIG,
    "ga": GA_CONFIG,
    "gads": GADS_CONFIG,
    "meta": META_CONFIG
}


def get_preprocessing_config(source_name: str) -> PreprocessingConfig:
    """Get preprocessing configuration for a source."""
    if source_name not in PREPROCESSING_CONFIGS:
        raise ValueError(f"Unknown preprocessing source: {source_name}")
    return PREPROCESSING_CONFIGS[source_name]


def list_preprocessing_sources() -> List[str]:
    """List all available preprocessing sources."""
    return list(PREPROCESSING_CONFIGS.keys())
