from sqlalchemy.orm import Session
from app.models import AggregatedMarketPrice, MarketRate
import numpy as np
from sqlalchemy.sql import func


def calculate_percentiles(prices):
    prices_sorted = np.sort(prices)
    prices_sorted_float = [float(price) for price in prices_sorted]
    percentile_10 = np.percentile(prices_sorted_float, 10)
    median = np.percentile(prices_sorted_float, 50)
    percentile_90 = np.percentile(prices_sorted_float, 90)
    return percentile_10, median, percentile_90


def calculate_aggregated_prices(db: Session):
    """
    This function calculates aggregated market prices (min, max, percentiles, median)
    from the raw market data and updates the aggregated_market_rates table.
    """

    results = db.query(
        MarketRate.date,
        MarketRate.origin,
        MarketRate.destination,
        func.min(MarketRate.price).label("min_price"),
        func.max(MarketRate.price).label("max_price"),
    ).group_by(MarketRate.date, MarketRate.origin, MarketRate.destination).all()
    

    for record in results:
        # Fetch prices for the current group (date, origin, destination)
        prices = db.query(MarketRate.price).filter(
            MarketRate.date == record.date,
            MarketRate.origin == record.origin,
            MarketRate.destination == record.destination
        ).all()
        # Extract prices from the list of tuples
        prices = [price[0] for price in prices]
        # Calculate percentiles
        percentile_10, median, percentile_90 = calculate_percentiles(prices)

        # Insert the aggregated data into the `aggregated_market_prices` table
        db.add(AggregatedMarketPrice(
            date=record.date,
            origin=record.origin,
            destination=record.destination,
            min_price=record.min_price,
            percentile_10_price=percentile_10,
            median_price=median,
            percentile_90_price=percentile_90,
            max_price=record.max_price
        ))

    db.commit()
    return {"status": "Aggregated data inserted successfully"}
