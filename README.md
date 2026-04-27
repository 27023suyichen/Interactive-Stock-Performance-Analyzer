# 📈 Stock Performance Analyzer

**ACC102 Mini Assignment - Track 4: Interactive Data Analysis Tool**

---

## 📋 Project Overview

This project is an interactive stock performance analysis tool designed for individual investors, finance students, and small business owners. The tool provides comprehensive analysis of stock performance metrics including price trends, volatility, risk-return profiles, and correlation analysis.

### Target Users
- Individual investors seeking quick stock performance comparison
- Finance students learning about stock analysis
- Small business owners considering stock investments

---

## 🚀 Key Features

- **Multi-Stock Analysis**: Analyze 7 major US stocks across 4 different sectors (Technology, Finance, Consumer, Healthcare).
- **Interactive Dashboard**: Real-time data visualization built with Streamlit.
- **Comprehensive Metrics (5 Tabs)**:
  - *Price Trends*: Normalized performance, Moving Averages, Bollinger Bands, Return comparisons.
  - *Statistics*: Descriptive stats, Price distribution box plots, CSV export.
  - *Risk Analysis*: Volatility, Sharpe Ratio, Max Drawdown, Risk-Return scatter plot.
  - *Correlation*: Dynamic correlation heatmap with automated insights.
  - *Summary*: Auto-generated performance highlights and investment insights.
- **Fault Tolerance**: Automatically falls back to offline backup data if the Yahoo Finance API rate-limits the request, ensuring the app never crashes.

---

## 📁 Project Structure

```text
acc102-stock-analyzer/
├── README.md                # Project documentation
├── LICENSE                  # Project license
├── requirements.txt         # Python dependencies
├── app.py                   # Streamlit web application
├── notebook.ipynb           # Jupyter Notebook analysis
└── data/                    # Data directory
    └── sample_stock_prices.csv  # Offline backup for rate-limit protection
```

---

## 🛠️ Technical Stack

| Library | Purpose |
|---------|---------|
| **Python 3.8+** | Core language |
| **Streamlit** | Interactive web framework |
| **pandas** | Data manipulation and analysis |
| **numpy** | Numerical computation |
| **matplotlib** | Data visualization |
| **seaborn** | Statistical visualization |
| **yfinance** | Yahoo Finance historical data API |

---

## 🔧 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/acc102-stock-analyzer.git
cd acc102-stock-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Running the Streamlit App
1. Ensure you are in the project root directory.
2. Run the following command:
```bash
streamlit run app.py
```
3. The application will open automatically in your web browser (usually at `http://localhost:8501`).

### How to Use the App
1. **Sidebar - Stock Selection**: Choose from 7 stocks using the multi-select dropdown (default: AAPL, MSFT, JPM).
2. **Sidebar - Time Period**: Select a timeframe from 1 Month to 2 Years.
3. **Sidebar - Analysis Options**: Toggle Moving Averages (10/20/50/100/200-day) and Bollinger Bands.
4. **Tab 1 - Price Trends**: View normalized performance charts, individual stock technical indicators, and total return comparisons.
5. **Tab 2 - Statistics**: View descriptive statistics table and price distribution box plots. Download results as CSV.
6. **Tab 3 - Risk Analysis**: View risk metrics, risk-return scatter plot, and volatility comparison.
7. **Tab 4 - Correlation**: View correlation heatmap and automated correlation insights (requires 2+ stocks).
8. **Tab 5 - Summary**: View auto-generated performance highlights, risk analysis, and investment insights.

---

## 📊 Data Source & Robustness

- **Primary Source**: Yahoo Finance (via `yfinance` library).


**Stocks Included:**

| Ticker | Company | Sector |
|--------|---------|--------|
| AAPL | Apple Inc. | Technology |
| MSFT | Microsoft Corporation | Technology |
| JPM | JPMorgan Chase & Co. | Finance |
| BAC | Bank of America Corp. | Finance |
| KO | The Coca-Cola Company | Consumer |
| WMT | Walmart Inc. | Consumer |
| JNJ | Johnson & Johnson | Healthcare |

---

## 🔒 Limitations

1. **Data Limitations**: Analysis based on historical data; past performance does not guarantee future results
2. **Simplified Metrics**: Sharpe ratio uses simplified calculation with assumed risk-free rate (5%)
3. **Limited Stocks**: Only 7 stocks analyzed; results may not represent broader market
4. **No Transaction Costs**: Analysis does not account for trading fees or taxes

---

## 📄 License

This project is created for educational purposes as part of the ACC102 Mini Assignment.

---

## 👤 Author

- **Course**: ACC102 - Mini Assignment
- **Track**: Track 4 - Interactive Data Analysis Tool
- **Date**: April 2026

---

## 🙏 Acknowledgments

- Yahoo Finance for providing free stock data
- Streamlit for the interactive web framework
- XJTLU IBSS for the assignment guidance

