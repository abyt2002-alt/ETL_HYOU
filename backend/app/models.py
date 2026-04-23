from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, index=True)
    trigger_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    triggered_by = Column(String(100), default="system")
    summary_message = Column(Text, nullable=True)

    items = relationship("IngestionRunItem", back_populates="run")


class IngestionRunItem(Base):
    __tablename__ = "ingestion_run_items"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("ingestion_runs.id"), nullable=False)
    source_name = Column(String(100), nullable=False)
    sheet_tab_name = Column(String(100), nullable=False)
    target_table_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    rows_read = Column(Integer, default=0)
    rows_loaded = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    run = relationship("IngestionRun", back_populates="items")


class RawMeta(Base):
    __tablename__ = "raw_meta"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    dma_region = Column(String(255))
    impressions = Column(Integer)
    amount_spent = Column(Numeric(10, 2))
    ingested_at = Column(DateTime, default=datetime.utcnow)


class RawShopify(Base):
    __tablename__ = "raw_shopify"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    shipping_postal_code = Column(String(50))
    order = Column(String(100))
    customer_type = Column(String(100))
    net_sales = Column(Numeric(10, 2))
    order_item_current_quantity = Column(Integer)
    orders = Column(Integer)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class RawGA(Base):
    __tablename__ = "raw_ga"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    region = Column(String(255))
    session_source = Column(String(500))
    city = Column(String(255))
    sessions = Column(Integer)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class RawGAds(Base):
    __tablename__ = "raw_gads"

    id = Column(Integer, primary_key=True, index=True)
    campaign = Column(String(500))
    day = Column(Date, nullable=False)
    cost = Column(Numeric(10, 2))
    impr_ = Column(Integer)  # "Impr." becomes "impr_"
    ingested_at = Column(DateTime, default=datetime.utcnow)


# Preprocessing operational tables

class MappingFile(Base):
    __tablename__ = "mapping_files"

    id = Column(Integer, primary_key=True, index=True)
    mapping_name = Column(String(100), nullable=False)
    source_name = Column(String(100), nullable=False)
    mapping_type = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    required_columns = Column(Text, nullable=False)
    is_active = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), default="system")
    notes = Column(Text, nullable=True)


class PreprocessingRun(Base):
    __tablename__ = "preprocessing_runs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    triggered_by = Column(String(100), default="system")
    summary_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PreprocessingRunItem", back_populates="run")


class PreprocessingRunItem(Base):
    __tablename__ = "preprocessing_run_items"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("preprocessing_runs.id"), nullable=False)
    source_name = Column(String(100), nullable=False)
    input_table = Column(String(100), nullable=False)
    output_table = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    rows_read = Column(Integer, default=0)
    rows_output = Column(Integer, default=0)
    exact_duplicates_found = Column(Integer, default=0)
    business_duplicates_found = Column(Integer, default=0)
    mapping_matches = Column(Integer, default=0)
    mapping_unmatched = Column(Integer, default=0)
    unlabeled_count = Column(Integer, default=0)
    issues_found = Column(Integer, default=0)
    mapping_file_id = Column(Integer, ForeignKey("mapping_files.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    run = relationship("PreprocessingRun", back_populates="items")
    mapping_file = relationship("MappingFile")


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id = Column(Integer, primary_key=True, index=True)
    run_item_id = Column(Integer, ForeignKey("preprocessing_run_items.id"), nullable=False)
    source_name = Column(String(100), nullable=False)
    issue_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    row_identifier = Column(String(255), nullable=True)
    issue_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run_item = relationship("PreprocessingRunItem")


# Curated tables

class CuratedShopify(Base):
    __tablename__ = "curated_shopify"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    shipping_postal_code = Column(String(50))
    shipping_postal_code_cleaned = Column(String(50))
    order = Column(String(100))
    customer_type = Column(String(100))
    net_sales = Column(Numeric(10, 2))
    order_item_current_quantity = Column(Integer)
    orders = Column(Integer)
    dma = Column(String(255))
    processed_at = Column(DateTime, default=datetime.utcnow)


class CuratedGA(Base):
    __tablename__ = "curated_ga"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    region = Column(String(255))
    session_source = Column(String(500))
    city = Column(String(255))
    sessions = Column(Integer)
    dma = Column(String(255))
    source_label = Column(String(100))
    processed_at = Column(DateTime, default=datetime.utcnow)


class CuratedGAds(Base):
    __tablename__ = "curated_gads"

    id = Column(Integer, primary_key=True, index=True)
    campaign = Column(String(500))
    day = Column(Date, nullable=False)
    cost = Column(Numeric(10, 2))
    impr = Column(Integer)
    processed_at = Column(DateTime, default=datetime.utcnow)


class CuratedMeta(Base):
    __tablename__ = "curated_meta"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Date, nullable=False)
    dma_region = Column(String(255))
    impressions = Column(Integer)
    amount_spent = Column(Numeric(10, 2))
    processed_at = Column(DateTime, default=datetime.utcnow)
