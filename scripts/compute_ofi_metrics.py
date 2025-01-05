import pandas as pd
import numpy as np

def compute_ofi(df: pd.DataFrame, levels: int = 5) -> pd.DataFrame:
    """
    Compute multi-level OFI metrics for a given order book DataFrame.
    
    Parameters
    ----------
    df: DataFrame
        Data containing bid/ask prices and volumes.
    levels: int
        Number of levels to compute OFI for.
        
    Returns
    -------
    DataFrame
        OFI metrics for each level.
    """
    ofi_metrics = {}
    for level in range(1, levels + 1):
        bid_col, ask_col = f"bid_vol_{level}", f"ask_vol_{level}"
        ofi_metrics[f"OFI_{level}"] = df[bid_col].diff() - df[ask_col].diff()
    return pd.DataFrame(ofi_metrics)

def integrate_ofi_with_pca(ofi_df: pd.DataFrame) -> pd.Series:
    """
    Apply PCA to multi-level OFI metrics.
    
    Parameters
    ----------
    ofi_df: DataFrame
        Multi-level OFI DataFrame.
        
    Returns
    ----------
    Series
        Integrated multi-level OFIs using PCA.
    """
    from sklearn.decomposition import PCA
    
    pca = PCA(n_components=1)
    integrated_ofi = pca.fit_transform(ofi_df.dropna())
    return pd.Series(integrated_ofi.flatten(), index=ofi_df.index, name="PCA_OFI")

if __name__ == "__main__":
    stock_data = pd.read_csv("data/AAPL.csv")
    ofi = compute_ofi(stock_data)
    pca_ofi = integrate_ofi_with_pca(ofi)
    print(pca_ofi.head())
