import pandas as pd
import numpy as np
from typing import Dict, Tuple

def compute_order_flow(book_updates: pd.DataFrame, levels: int) -> Tuple[Dict[int, pd.Series], Dict[int, pd.Series]]:
    """
    Compute bid and ask order flows at each level of the order book.
    
    Parameters
    ----------
        book_updates: pd.DataFrame
            DataFrame containing order book updates with columns for bid and ask prices/sizes.
        levels: int
            Number of levels in the order book to consider.

    Returns
    ----------
        Tuple[Dict[int, pd.Series], Dict[int, pd.Series]]
            Dictionaries containing bid and ask order flows for each level.
    """
    of_bid = {}
    of_ask = {}
    for level in range(1, levels + 1):
        of_bid[level] = book_updates[f'bid_size_{level}'].diff()
        of_ask[level] = -book_updates[f'ask_size_{level}'].diff()

        of_bid[level][book_updates[f'bid_price_{level}'].diff() < 0] = 0
        of_ask[level][book_updates[f'ask_price_{level}'].diff() > 0] = 0
    return of_bid, of_ask

def compute_best_level_ofi(of_bid, of_ask):
    best_ofi = of_bid[1] - of_ask[1]
    return best_ofi.cumsum()

def compute_deeper_level_ofi(of_bid: Dict[int, pd.Series], of_ask: Dict[int, pd.Series], levels: int) -> Dict[int, pd.Series]:
    """
    Compute the deeper-level Order Flow Imbalance (OFI) for each level.
    
    Parameters
    ----------
        of_bid: (Dict[int, pd.Series])
            Bid order flows for each level.
        of_ask: (Dict[int, pd.Series])
            Ask order flows for each level.
        levels: int
            Number of levels in the order book to consider.

    Returns
    ----------
        Dict[int, pd.Series]
            Cumulative deeper-level OFI for each level over time.
    """
    deeper_ofi = {}
    for level in range(1, levels + 1):
        deeper_ofi[level] = (of_bid[level] - of_ask[level]).cumsum()
    return deeper_ofi

def compute_multi_level_ofi(deeper_ofi: Dict[int, pd.Series], levels: int) -> np.ndarray:
    """
    Compute the multi-level OFI vector by stacking deeper-level OFIs for all levels.
    
    Parameters
    ----------
        deeper_ofi: Dict[int, pd.Series]
            Cumulative deeper-level OFI for each level.
        levels: int
            Number of levels in the order book to consider.

    Returns
    ----------
        np.ndarray: Multi-level OFI vector (time series) with shape (n_samples, levels).
    """
    multi_level_ofi = np.vstack([deeper_ofi[level] for level in range(1, levels + 1)]).T
    return multi_level_ofi

def compute_average_depth(book_updates: pd.DataFrame, levels: int) -> np.ndarray:
    """
    Compute the average order book depth used to scale the OFI.
    
    Parameters
    ----------
        book_updates: pd.DataFrame
            DataFrame containing order book updates with size columns for bid and ask sides.
        levels: int
            Number of levels in the order book to consider.

    Returns
    ----------
        np.ndarray
            Average depth for scaling OFI at each level.
    """
    avg_depths = []
    for level in range(1, levels + 1):
        avg_depth = book_updates[[f'bid_size_{level}', f'ask_size_{level}']].mean(axis=1).mean()
        avg_depths.append(avg_depth)
    return np.array(avg_depths)


def scale_ofi(multi_level_ofi: np.ndarray, avg_depths: np.ndarray) -> np.ndarray:
    """
    Scale the multi-level OFI by the average order book depth.
    
    Parameters
    ----------
        multi_level_ofi (np.ndarray): Multi-level OFI vector (time series).
        avg_depths (np.ndarray): Average depth for scaling.

    Returns
    ----------
        np.ndarray: Scaled multi-level OFI vector.
    """
    scaled_ofi = multi_level_ofi / avg_depths
    return scaled_ofi


def calculate_ofi(book_updates: pd.DataFrame, levels: int = 5) -> Tuple[pd.Series, np.ndarray]:
    """
    Calculate the best-level and multi-level Order Flow Imbalance (OFI) metrics.
    
    Parameters
    ----------
        book_updates: pd.DataFrame
            DataFrame containing order book updates with bid/ask sizes and prices.
        levels: int, optional
            Number of levels in the order book to consider. Default is 5.

    Returns
    ----------
        Tuple[pd.Series, np.ndarray]
            Best-level OFI (cumulative) and scaled multi-level OFI vector.
    """
    of_bid, of_ask = compute_order_flow(book_updates, levels)
    best_ofi = compute_best_level_ofi(of_bid, of_ask)
    deeper_ofi = compute_deeper_level_ofi(of_bid, of_ask, levels)
    multi_level_ofi = compute_multi_level_ofi(deeper_ofi, levels)
    avg_depths = compute_average_depth(book_updates, levels)
    scaled_ofi = scale_ofi(multi_level_ofi, avg_depths)
    return best_ofi, scaled_ofi

def integrate_ofi_with_pca(multi_level_ofi: np.ndarray) -> np.ndarray:
    """
    Integrate multi-level OFIs into a single metric using Principal Component Analysis (PCA).
    
    Parameters
    ----------
        multi_level_ofi: np.ndarray
            Multi-level OFI matrix with shape (n_samples, n_levels).
    
    Returns
    ----------
        np.ndarray
            Integrated OFI time series as a single metric.
    """
    pca = PCA(n_components=1)
    pca.fit(multi_level_ofi)

    w1 = pca.components_[0]
    w1_normalized = w1 / np.sum(np.abs(w1))
    
    integrated_ofi = np.dot(multi_level_ofi, w1_normalized)
    return integrated_ofi

if __name__ == "__main__":
    stock_data = pd.read_csv("data/AAPL.csv")

    # derive multi-level OFI metrics (up to 5 levels)
    levels = 5

    best_ofi, multi_level_ofi = calculate_ofi(stock_data, levels)
    integrated_ofi = integrate_ofi_with_pca(multi_level_ofi)

    print("Best-Level OFI (Cumulative):")
    print(best_ofi.head())

    print("\nIntegrated Multi-Level OFI (using PCA):")
    print(integrated_ofi[:10])