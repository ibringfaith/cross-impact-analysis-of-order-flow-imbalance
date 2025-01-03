import databento as db
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from sklearn.decomposition import PCA

def initialize_databento_client(api_key):
    """
    Initializes and returns a Databento client using the provided API key
    """
    return db.Client(api_key=api_key)

def fetch_mbp10_data(client, stock, start_date=None, end_date=None):
    """
    Fetches MBP-10 data for the given stock using the MBP-10 data schema provided by Databento
    
    Parameters:
    - client: The Databento client instance
    - stock: The stock symbol
    - start_date: The start date for fetching data in YYYY-MM-DD format
    - end_date: The end date for fetching data in YYYY-MM-DD format
    
    Returns:
    - DataFrame containing the MBP-10 data for the specified stock
    """
    data = client.mbp10(symbols=[stock], start=start_date, end=end_date)
    return data

def preprocess_data(data):
    """
    Preprocesses the raw MBP-10 data by performing transformations.
    
    Parameters:
    - data: The raw MBP-10 data to be preprocessed
    
    Returns:
    - Processed DataFrame
    """
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['OFI'] = data['ask_size'] - data['bid_size']
    data.fillna(0, inplace=True)
    return data

def apply_pca(data, n_components=3):
    """
    Integrate multi-level OFIs from data into a single metric using Principal Component Analysis (PCA)
    
    Parameters:
    - data: The data to apply PCA on
    - n_components: Number of components to keep after dimensionality reduction
    
    Returns:
    - DataFrame with PCA components as new features
    """
    pca = PCA(n_components=n_components)
    pca_components = pca.fit_transform(data[['OFI']].values)
    pca_df = pd.DataFrame(pca_components, columns=[f'PC{i+1}' for i in range(n_components)])
    data = pd.concat([data, pca_df], axis=1)
    
    return data

def save_processed_data(data, filename):
    """
    Saves the processed data to a CSV file.
    
    Parameters:
    - data: The processed data (as a DataFrame).
    - filename: The file path to save the data (including file extension).
    """
    data.to_csv(filename, index=False)
    print(f"Processed data saved to {filename}")

def fetch_process_and_save_data(client, stocks, start_date, end_date):
    """
    Fetches, preprocesses, and saves data for multiple stocks
    
    Parameters:
    - client: The Databento client instance
    - stocks: List of stocks to fetch data for
    - start_date: The start date for fetching data in YYYY-MM-DD format
    - end_date: The end date for fetching data in YYYY-MM-DD format
    """
    os.makedirs('data', exist_ok=True)  # Ensure the directory exists
    
    for stock in stocks:
        print(f"Fetching data for {stock}...")
        raw_data = fetch_mbp10_data(client, stock, start_date, end_date)
        df = pd.DataFrame(raw_data)
        processed_data = preprocess_data(df)
        processed_data_with_pca = apply_pca(processed_data)
        save_processed_data(processed_data_with_pca, f'data/{stock}_processed_data.csv')

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('API_KEY')
    client = initialize_databento_client(api_key)

    # 10 Nasdaq 100 stocks representing various sectors
    tickers = ['AAPL', 'MSFT', 'NVDA', 'AMGN', 'GILD', 'TSLA', 'PEP', 'JPM', 'V', 'XOM']

    start_date = '2022-01-01'
    end_date = '2024-12-31'

    fetch_process_and_save_data(client, tickers, start_date, end_date)
