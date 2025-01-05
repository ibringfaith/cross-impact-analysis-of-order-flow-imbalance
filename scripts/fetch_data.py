import databento as db
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

def initialize_databento_client(api_key: str) -> db.Historical:
    """
    Initializes and returns a Databento client using the provided API key.
    """
    return db.Historical(api_key)

def fetch_mbp10_data(client: db.Historical, stock: str, start_date: str = None, end_date: str = None, dataset: str = 'XNAS.ITCH') -> pd.DataFrame:
    """
    Fetches MBP-10 data for the given stock using the MBP-10 data schema provided by Databento.
    
    Parameters
    ----------
    client: Historical
        The Databento client instance.
    stock: str
        The stock symbol.
    start_date: str, optional
        The start date for fetching data in YYYY-MM-DD format.
    end_date: str, optional
        The end date for fetching data in YYYY-MM-DD format.
    dataset: str
        Dataset to fetch.
    
    Returns
    ----------
    pd.DataFrame
        The MBP-10 data for the specified stock.
    """
    try:
        data = client.timeseries.get_range(
            dataset=dataset,
            symbols=[stock],
            schema="mbp-10",
            start=start_date,
            end=end_date
            )
        df = data.to_df()
        return df
    except db.common.error.BentoClientError as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()


def save_data(data: pd.DataFrame, filename: str):
    """
    Saves the data to a CSV file.
    
    Parameters
    ----------
    data: pd.DataFrame
        The stock data.
    - filename: str
        The file path to save the data.
    """
    data.to_csv(filename, index=False)
    print(f"Processed data saved to {filename}")

def fetch_and_save_data(client: db.Historical, stocks: list[str], start_date: str, end_date: str, dataset: str = 'XNAS.ITCH'):
    """
    Fetches and saves data for the given stocks.
    
    Parameters
    ----------
    client: Historical
        Databento client instance.
    stocks: list[str]
        List of stocks to fetch data for.
    start_date: str
        The start date for fetching data in YYYY-MM-DD format.
    end_date: str
        The end date for fetching data in YYYY-MM-DD format.
    """
    os.makedirs('data', exist_ok=True)
    
    for stock in stocks:
        print(f"Fetching data for {stock}...")
        data = fetch_mbp10_data(client, stock, start_date, end_date)
        df = pd.DataFrame(raw_data)
        save_processed_data(processed_data_with_pca, f'data/{stock}.csv')

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('API_KEY')
    client = initialize_databento_client(api_key)

    # 5 Nasdaq 100 stocks representing various sectors
    stocks = ["AAPL", "AMGN", "TSLA", "JPM", "XOM"]

    # use the Nasdaq ITCH data
    dataset="XNAS.ITCH"
    start_date = '2024-11-04'
    end_date = '2024-11-12'

    fetch_and_save_data(client, stocks, start_date, end_date, dataset)
