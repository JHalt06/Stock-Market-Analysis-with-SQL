import os
import pandas as pd
import requests
from dotenv import load_dotenv
from src.utils.db_utils import exec_commit
from src.utils.db_utils import exec_sql_file

exec_sql_file("../../sql/schema.sql") #make sure table exists before inserting
#Load environment vars
load_dotenv() #reads the .env and sets each line as an environment variable

API_KEY = os.getenv("ALPHA_VANTAGE_KEY") #retreives the value of the api key from the .env

def ingest_stock(symbol):
    print("Getting data for: " + symbol + "...")
#API Call
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url) #Sends an HTTP GET request to the API
    data = response.json() #Parses the JSON response into a Python dictionary

#CONVERT raw API responses into the correct format for the tables.
#JSON to DataFrame
    time_series = data.get("Time Series (5min)", {}) #Extracts the dictionary containing the actual time series data, Keys = timestamps, values = OHLCV data
    if not time_series:
        print("ERROR: No data returned for " + symbol)
        return
    df = pd.DataFrame.from_dict(time_series, orient="index") #Converts the dictionary into a DataFrame. 
    df.reset_index(inplace=True) #Moves the "index"(timestamps) into a regular column
    df.rename(columns={"index":"timestamp"}, inplace=True) #Rename the new column from "index" to "timestamp"

    #Add a column for symbol
    df["symbol"] = symbol #Add a column with the stock ticker so multiple stocks can be stored in the table.

#Rename the columns to match the DB schema
    df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume",
    }, inplace=True)

    print(df.head())#check before inserting

#Insert into PostgresSQL
    try:
        for _, row in df.iterrows(): #Go through each row of the pandas DataFrame df
    #itterrows() returns (index, row) pairs. _ ignores the index since you don't need it here
    #row is a pandas Series containing the data for one timestamp
            exec_commit("""
                INSERT INTO stock_data(symbol,timestamp,open,high,low,close,volume)
                    VALUES(%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp) DO NOTHING;
            """, ( #This is a tuple of actual values from the DataFrame row:
                row["symbol"],
                row["timestamp"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
            )) #passes the row[] column of that specific row into the %s. 
        print(f"Inserted {len(df)} rows for" + symbol) #Ex: Inserted 4032 rows for AAPL
    except Exception as e:
        print("Error inserting the data:", e)

#Ex use
if __name__ == "__main__":
    symbols = ["BAC", "ASTS", "CSCO"]
    for symbol in symbols:
        ingest_stock(symbol)
#Next Step: 
#Wrap it in a function that takes (symbol) as a parameter
#Loop over a list of symbols to ingest multiple stocks. def ingest_stock(symbol)