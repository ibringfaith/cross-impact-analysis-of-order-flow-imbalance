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
    return db.Historical(api_key)

def fetch_mbp10_data(client, stock, start_date=None, end_date=None, dataset='XNAS.ITCH'):
    """
    Fetches MBP-10 data for the given stock using the MBP-10 data schema provided by Databento
    
    Parameters:
    - client: The Databento client instance
    - stock: The stock symbol
    - start_date: The start date for fetching data in YYYY-MM-DD format
    - end_date: The end date for fetching data in YYYY-MM-DD format
    - dataset: Dataset to fetch
    
    Returns:
    - DataFrame containing the MBP-10 data for the specified stock
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

def derive_multi_level_ofi(data, num_levels=5):
    """
    Derives multi-level Order Flow Imbalance (OFI) for the given data
    
    Parameters:
    - data: The MBP-10 data as a DataFrame
    - num_levels: The number of levels to derive OFI for
    
    Returns:
    - DataFrame with OFI metrics for each level
    """
    ofi_metrics = []
    
    for level in range(1, num_levels + 1):
        bid_col = f'bid_size_{level}'
        ask_col = f'ask_size_{level}'
        data[f'OFI_level_{level}'] = data[ask_col] - data[bid_col]
        ofi_metrics.append(f'OFI_level_{level}')
    
    return data[ofi_metrics]

def apply_pca(ofi_data, n_components=1):
    """
    Apply PCA to reduce the dimensionality of multi-level OFI metrics
    
    Parameters:
    - ofi_data: The OFI metrics to apply PCA on
    - n_components: The number of principal components to keep
    
    Returns:
    - DataFrame with the PCA components
    """
    pca = PCA(n_components=n_components)
    pca_components = pca.fit_transform(ofi_data)
    pca_df = pd.DataFrame(pca_components, columns=[f'PC{i+1}' for i in range(n_components)])
    
    return pca_df

def preprocess_data(data):
    """
    Preprocesses the raw MBP-10 data by performing transformations
    
    Parameters:
    - data: The raw MBP-10 data to be preprocessed
    
    Returns:
    - Processed DataFrame with multi-level OFI and PCA components
    """
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    ofi_data = compute_multi_level_ofi(data)
    pca_df = apply_pca(ofi_data)
    data = pd.concat([data, pca_df], axis=1)
    data.fillna(0, inplace=True)
    return data

def save_processed_data(data, filename):
    """
    Saves the processed data to a CSV file.
    
    Parameters:
    - data: The processed data
    - filename: The file path to save the data
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
    os.makedirs('data', exist_ok=True)
    
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
    stocks = ['AAPL', 'MSFT', 'NVDA', 'AMGN', 'GILD', 'TSLA', 'PEP', 'JPM', 'V', 'XOM']

    # use the Nasdaq ITCH data
    dataset="XNAS.ITCH"
    start_date = '2022-01-01'
    end_date = '2024-12-31'

    fetch_process_and_save_data(client, stocks, start_date, end_date, dataset)
