from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body, Query
from sqlalchemy.orm import Session
import pandas as pd
from app.database import Base, engine, get_db
from app.models import UserRate, MarketRate,AggregatedMarketPrice
from app.crud import calculate_aggregated_prices
from typing import List
from datetime import date
from fastapi.middleware.cors import CORSMiddleware



# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend from localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...), user_email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Uploads and processes the CSV file into the 'user_rates' table.
    """

    try:
        df = pd.read_excel(file.file, header=0)
        required_columns = {"origin", "destination", "effective_date", "expiry_date", "price", "annual_volume"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Invalid CSV format")

        # Insert rows into the database
        for _, row in df.iterrows():
            user_rate = UserRate(
                user_email=user_email,
                origin=row["origin"],
                destination=row["destination"],
                effective_date=row["effective_date"],
                expiry_date=row["expiry_date"],
                price=row["price"],
                annual_volume=row["annual_volume"]
            )
            db.add(user_rate)
        db.commit()
        return {"message": "CSV uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_market_data/")
async def upload_market_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint to upload a CSV file containing raw market data. 
    The data is processed, stored in the `market_rates` table, 
    and aggregated data is calculated and stored in the `aggregated_market_rates` table.
    """
    
    df = pd.read_excel(file.file, header=0)

    # Validate and process the CSV data
    if not all(col in df.columns for col in ["date", "origin", "destination", "price"]):
        return {"error": "CSV must contain 'date', 'origin', 'destination', and 'price' columns."}
    
    # Insert raw data into `market_rates` table
    for index, row in df.iterrows():
        market_rate = MarketRate(
            date=pd.to_datetime(row["date"]).date(),
            origin=row["origin"],
            destination=row["destination"],
            price=row["price"]
        )
        db.add(market_rate)
    
    db.commit()  # Commit the raw data insertion

    # After uploading, calculate the aggregated data and insert it into `aggregated_market_rates`
    df['date'] = pd.to_datetime(df['date'])
    aggregated_data_status = calculate_aggregated_prices(db)

    return {"message": aggregated_data_status}




@app.get("/fetch_user_rates/", response_model=List[dict])
async def fetch_user_rates(
    db: Session = Depends(get_db), 
    user_email: str = Query(..., description="The email of the user whose rates we are fetching"),
    target_date: date = Query(None, description="The target date for which we want to fetch the rates")
):
    """
    Fetch aggregated market rates and user rates for a specific user, then calculate potential savings.
    """
    try:
        # Query the aggregated market data for the given date
        aggregated_data = db.query(
            AggregatedMarketPrice.date,
            AggregatedMarketPrice.origin,
            AggregatedMarketPrice.destination,
            AggregatedMarketPrice.min_price,
            AggregatedMarketPrice.percentile_10_price,
            AggregatedMarketPrice.median_price,
            AggregatedMarketPrice.percentile_90_price,
            AggregatedMarketPrice.max_price
        )
        
        if target_date:
            aggregated_data = aggregated_data.filter(AggregatedMarketPrice.date == target_date)
        
        aggregated_data = aggregated_data.all()

        # Query the user rates for the specific email and the same date
        user_data = db.query(
            UserRate.user_email,
            UserRate.origin,
            UserRate.destination,
            UserRate.effective_date,
            UserRate.expiry_date,
            UserRate.price,
            UserRate.annual_volume
        ).filter(UserRate.user_email == user_email,
                 target_date >= UserRate.effective_date,
                 target_date <= UserRate.expiry_date).all()

        results = []

        for user_row in user_data:
            # Find matching aggregated market rates for the current user's origin and destination
            matching_aggregated_rates = [
                agg_row for agg_row in aggregated_data
                if agg_row.origin == user_row.origin and agg_row.destination == user_row.destination
            ]

            for agg_row in matching_aggregated_rates:
                savings_data = {
                    "date": agg_row.date,
                    "user_email": user_row.user_email,
                    "origin": agg_row.origin,
                    "destination": agg_row.destination,
                    "user_price": user_row.price,
                    "min_price": agg_row.min_price,
                    "percentile_10_price": agg_row.percentile_10_price,
                    "median_price": agg_row.median_price,
                    "percentile_90_price": agg_row.percentile_90_price,
                    "max_price": agg_row.max_price,
                    "potential_savings_min_price": (agg_row.min_price - user_row.price) * user_row.annual_volume,
                    "potential_savings_percentile_10_price": (agg_row.percentile_10_price - user_row.price) * user_row.annual_volume,
                    "potential_savings_median_price": (agg_row.median_price - user_row.price) * user_row.annual_volume,
                    "potential_savings_percentile_90_price": (agg_row.percentile_90_price - user_row.price) * user_row.annual_volume,
                    "potential_savings_max_price": (agg_row.max_price - user_row.price) * user_row.annual_volume
                }
                results.append(savings_data)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))