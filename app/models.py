from sqlalchemy import Column, Integer, String, Date, DECIMAL
from app.database import Base

class MarketRate(Base):
    __tablename__ = "market_rates"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

class AggregatedMarketPrice(Base):
    __tablename__ = "aggregated_market_prices"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    min_price = Column(DECIMAL(10, 2))
    percentile_10_price = Column(DECIMAL(10, 2))
    median_price = Column(DECIMAL(10, 2))
    percentile_90_price = Column(DECIMAL(10, 2))
    max_price = Column(DECIMAL(10, 2))

class UserRate(Base):
    __tablename__ = "user_rates"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    annual_volume = Column(DECIMAL(10, 2), nullable=False)
