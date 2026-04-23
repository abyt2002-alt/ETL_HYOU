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
