import os
import pandas as pd
import requests
import psycopg2
from dotenv import load_dotenv

#load environment variables
load_dotenv() #reads the .env and sets each line as an environment variable

API_KEY = os.getenv("ALPHA_VANTAGE_KEY") #retreives the value of the api key from the .env
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

symbol = "AAPL" #specific stock for testing

#API Call
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
response = requests.get(url) #Sends an HTTP GET request to the API
data = response.json() #Parses the JSON response into a Python dictionary

#CONVERT raw API responses into the correct format for the tables.
#JSON to DataFrame
time_series = data.get("Time Series (5min)", {}) #Extracts the dictionary containing the actual time series data, Keys = timestamps, values = OHLCV data
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
    conn = psycopg2.connect( #open a connection to the PostgreSQL db
        host=DB_HOST, #each parameter is pulled from the .env file via os.getenv()
        dbname=DB_NAME, 
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cur = conn.cursor() # A cursor lets you execute SQL commands through the connection
    #use cur.execute() to send SQL statements to the database
    for _, row in df.iterrows: #Go through each row of the pandas DataFrame df
#itterrows() returns (index, row) pairs. _ ignores the index since you don't need it here
#row is a pandas Series containing the data for one timestamp
        cur.execute("""
            INSERT INTO stock_prices(symbol,timestamp,open,high,low,close,volume)
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
        ))
    conn.commit() #Saves changes made in this session to the database
    cur.close()
    conn.close()
    print(f"Inserted {len(df)} rows for {symbol}")

except Exception as e:
    print("Error inserting the data:", e)

#Next Step: 
#Wrap it in a function that takes (symbol) as a parameter
#Loop over a list of symbols to ingest multiple stocks. def ingest_stock(symbol)