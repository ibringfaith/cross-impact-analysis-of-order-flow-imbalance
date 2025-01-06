# Work Trial Task: Cross-Impact Analysis of Order Flow Imbalance (OFI)

## Description of the task
I am provided with a subset of equity market data containing order book updates and trades for several highly liquid stocks. My objective is to:

1. #### Compute OFI Metrics:
   - Derive multi-level OFI metrics (up to 5 levels) for each stock in the dataset.
   - Integrate these multi-level OFIs into a single metric using Principal Component Analysis (PCA) or another dimensionality reduction method.
2. #### Analyze Cross-Impact:
   - Examine the contemporaneous cross-impact of OFI on short-term price changes across stocks.
   - Evaluate the predictive power of lagged cross-asset OFI on future price changes (e.g., 1-minute and 5-minute horizons).
3. #### Quantify Results:
   - Use regression models to assess the explanatory power of contemporaneous OFI and predictive power of lagged OFI.
   - Compare self-impact (within the same stock) vs. cross-impact (between stocks) in your models.
6. #### Visualization and Reporting:
   - Create visualizations (e.g., heatmaps, scatter plots) to illustrate cross-impact relationships and OFI trends.
   - Summarize my findings in a concise report.

## Steps to Run the Analysis
1. Clone the repository
```bash
git clone ibringfaith/cross-impact-analysis-of-order-flow-imbalance
```
2. Install Python packages used in the project
```bash
pip install -r requirements.txt
```
3. Run the script to fetch the data and save it to CSVs
```bash
python scripts/fetch_data.py
```
4. Run the script to perform compute OFI metrics.
```bash
python scripts/compute_ofi_metrics.py
```
5. Run the script to quantify and visualize the results.
```bash
python scripts/analyze_cross_impacts.py
```
## Brief summary of the findings
