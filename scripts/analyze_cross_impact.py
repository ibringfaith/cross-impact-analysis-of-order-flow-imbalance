import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

def cross_impact_analysis(ofi_df: pd.DataFrame, price_changes_df: pd.DataFrame) -> dict:
    """
    Perform cross-impact analysis using regression.
    
    Parameters
    ----------
        ofi_df: pd.DataFrame
            OFI metrics for multiple stocks.
        price_changes_df: pd.DataFrame
            Price changes for multiple stocks.
        
    Returns
    ----------
        dict: 
            Regression results including coefficients and R-squared values.
    """
    results = {}
    for target_stock in price_changes_df.columns:
        X = ofi_df.values
        y = price_changes_df[target_stock].values
        model = LinearRegression().fit(X, y)
        results[target_stock] = {
            "coefficients": model.coef_,
            "r_squared": model.score(X, y)
        }
    return results

def plot_heatmap(matrix: pd.DataFrame, title: str, output_file: str):
    """
    Plot a heatmap for cross-impact analysis.
    
    Parameters
    ----------
        matrix: DataFrame
            Cross-impact matrix.
        title: str
            Plot title.
        output_file: str
            Path to save the plot.
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title(title)
    plt.savefig(output_file)
    plt.show()

if __name__ == "__main__":
    ofi_data = pd.read_csv("results/OFI_metrics.csv")
    price_changes = pd.read_csv("results/price_changes.csv")
    
    analysis_results = cross_impact_analysis(ofi_data, price_changes)
    heatmap_data = pd.DataFrame({k: v["r_squared"] for k, v in analysis_results.items()})
    plot_heatmap(heatmap_data, "Cross-Impact Heatmap", "results/cross_impact_heatmap.png")
