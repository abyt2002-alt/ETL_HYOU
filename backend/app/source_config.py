from typing import List, Dict, Any, Optional


class SourceConfig:
    def __init__(
        self,
        source_name: str,
        sheet_tab_name: str,
        target_table_name: str,
        required_columns: List[str],
        optional_columns: List[str],
        field_types: Dict[str, str],
        date_fields: List[str],
        numeric_fields: List[str],
        load_mode: str = "replace",
        unique_keys: Optional[List[str]] = None,
        strict_columns: bool = False
    ):
        self.source_name = source_name
        self.sheet_tab_name = sheet_tab_name
        self.target_table_name = target_table_name
        self.required_columns = required_columns
        self.optional_columns = optional_columns
        self.field_types = field_types
        self.date_fields = date_fields
        self.numeric_fields = numeric_fields
        self.load_mode = load_mode  # "replace" or "upsert"
        self.unique_keys = unique_keys or []  # For upsert mode
        self.strict_columns = strict_columns  # Fail on unexpected columns

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "sheet_tab_name": self.sheet_tab_name,
            "target_table_name": self.target_table_name,
            "required_columns": self.required_columns,
            "optional_columns": self.optional_columns,
            "field_types": self.field_types,
            "date_fields": self.date_fields,
            "numeric_fields": self.numeric_fields,
            "load_mode": self.load_mode,
            "unique_keys": self.unique_keys,
            "strict_columns": self.strict_columns
        }


SOURCES = [
    SourceConfig(
        source_name="meta",
        sheet_tab_name="Meta",
        target_table_name="raw_meta",
        required_columns=["Day", "DMA region", "Impressions", "Amount spent"],
        optional_columns=[],
        field_types={
            "Day": "date",
            "DMA region": "string",
            "Impressions": "integer",
            "Amount spent": "numeric"
        },
        date_fields=["Day"],
        numeric_fields=["Amount spent"],
        load_mode="replace",  # Truncate and reload each run
        strict_columns=False
    ),
    SourceConfig(
        source_name="shopify",
        sheet_tab_name="Shopify",
        target_table_name="raw_shopify",
        required_columns=["Day", "Shipping postal code", "Order", "Customer type", 
                         "Net sales", "Order item current quantity", "Orders"],
        optional_columns=[],
        field_types={
            "Day": "date",
            "Shipping postal code": "string",
            "Order": "string",
            "Customer type": "string",
            "Net sales": "numeric",
            "Order item current quantity": "integer",
            "Orders": "integer"
        },
        date_fields=["Day"],
        numeric_fields=["Net sales"],
        load_mode="replace",  # Truncate and reload each run
        strict_columns=False
    ),
    SourceConfig(
        source_name="ga",
        sheet_tab_name="GA",
        target_table_name="raw_ga",
        required_columns=["Day", "Region", "Session source", "City", "Sessions"],
        optional_columns=[],
        field_types={
            "Day": "date",
            "Region": "string",
            "Session source": "string",
            "City": "string",
            "Sessions": "integer"
        },
        date_fields=["Day"],
        numeric_fields=[],
        load_mode="replace",  # Truncate and reload each run
        strict_columns=False
    ),
    SourceConfig(
        source_name="gads",
        sheet_tab_name="GAds",
        target_table_name="raw_gads",
        required_columns=["Campaign", "Day", "Cost", "Impr."],
        optional_columns=[],
        field_types={
            "Campaign": "string",
            "Day": "date",
            "Cost": "numeric",
            "Impr.": "integer"
        },
        date_fields=["Day"],
        numeric_fields=["Cost"],
        load_mode="replace",  # Truncate and reload each run
        strict_columns=False
    )
]


def get_source_config(source_name: str) -> SourceConfig:
    for source in SOURCES:
        if source.source_name == source_name:
            return source
    raise ValueError(f"Source '{source_name}' not found in configuration")


def get_all_sources() -> List[SourceConfig]:
    return SOURCES
