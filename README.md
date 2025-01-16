# Backend  API  for  CSV  Upload  and  Rate  Comparison

## Overview

This  project  provides  a  backend  API  for  uploading  CSV  files  containing  user  shipping  data,  fetching  aggregated  market  rates,  and  calculating  potential  savings.  The  backend  is  built  using  **FastAPI**,  **SQLAlchemy**,  and  **MySQL**.

### Features

- **CSV  Upload**:  Allows  users  to  upload  CSV  files  containing  shipping  data.
- **Market  Rate  Comparison**:  Retrieves  aggregated  market  prices  and  user-uploaded  rates.
- **Savings  Calculation**:  Computes  potential  savings  based  on  user  prices  and  market  prices.

## Requirements

- **Python  3.9+**
- **FastAPI**:  The  web  framework  for  the  API.
- **SQLAlchemy**:  ORM  for  database  interaction.
- **MySQL  8.0**:  Database  for  storing  the  data.
- **Pandas**:  For  handling  and  processing  CSV  files.

## Setup

### 1.  Clone  the  Repository

Clone  the  repository  to  your  local  machine:

### 2. Create and Activate a Virtual Environment
python  -m  venv  venv
.\venv\Scripts\activate


### 3. Install Dependencies

pip install fastapi uvicorn sqlalchemy pydantic mysqlclient python-multipart pandas openpyxl

### 4. Run the Backend Server

uvicorn app.main:app --reload

# API Endpoints

## 1. POST /upload_csv
This endpoint allows users to upload a CSV file containing their shipping data. The file is validated, and the data is stored in the users_rates table.

Request Body:

file: The CSV file containing user route data.
CSV Format Example:

```
user_email,origin,destination,effective_date,expiry_date,price,annual_volume
user@example.com,CNSHA,USLAX,2024-09-01,2025-09-01,1500,500
```

Response:

```
{
  "message":  "CSV  uploaded  and  data  stored  successfully."
}
```

## 2. GET /fetch_user_rates

This endpoint fetches the aggregated market rates and user-uploaded rates. It also calculates potential savings.

```
[
  {
    "date":  "2024-09-01",
    "origin":  "CNSHA",
    "destination":  "USLAX",
    "user_price":  1500,
    "min_price":  1300,
    "percentile_10_price":  1400,
    "median_price":  1450,
    "percentile_90_price":  1550,
    "max_price":  1600,
    "potential_savings_min_price":  100000,
    "potential_savings_percentile_10_price":  50000,
    "potential_savings_median_price":  25000,
    "potential_savings_percentile_90_price":  0,
    "potential_savings_max_price":  0
  }
]

```


## 3. POST /upload_market_data
This endpoint aggregates market data into percentiles (10th, median, 90th) and stores it in the aggregated_market_prices table.

Request Body:
```
{
  "date":  "2024-09-01",
  "origin":  "CNSHA",
  "destination":  "USLAX",
  "price":  1400
}
```
Response:
```
{
  "message":  "Market  data  aggregated  and  stored  successfully."
}

```


