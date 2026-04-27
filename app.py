"""
Stock Performance Analysis Tool
================================
An interactive Streamlit application for stock market analysis.


"""

import os
import time
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Stock Performance Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Define stock universe
STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'JPM': 'JPMorgan Chase & Co.',
    'BAC': 'Bank of America Corporation',
    'KO': 'The Coca-Cola Company',
    'WMT': 'Walmart Inc.',
    'JNJ': 'Johnson & Johnson'
}

SECTORS = {
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'JPM': 'Finance',
    'BAC': 'Finance',
    'KO': 'Consumer',
    'WMT': 'Consumer',
    'JNJ': 'Healthcare'
}


@st.cache_data(ttl=3600,show_spinner="Fetching stock data...")
def download_stock_data(tickers, start_date, end_date):
    """
    Download historical stock data from Yahoo Finance.
    
    Parameters:
    -----------
    tickers : list
        List of stock ticker symbols
    start_date : datetime
        Start date for historical data
    end_date : datetime
        End date for historical data
    
    Returns:
    --------
    DataFrame : Multi-index DataFrame with stock data
    """
    try:
        time.sleep(2)
        data = yf.download(
            tickers=tickers,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )
        if data.empty:
            st.warning("Downloaded data is empty. You might be rate-limited.Please try again later.")
        return data
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        return None


def extract_close_prices(data, tickers):
    """
    Extract and clean adjusted close prices.
    """
    if data is None or data.empty:
        return None
    
    # Get Adjusted Close prices
    if 'Adj Close' in data.columns.levels[0]:
        close_prices = data['Adj Close'].copy()
    else:
        close_prices = data['Close'].copy()
    
    # Handle single ticker case
    if len(tickers) == 1:
        close_prices = pd.DataFrame(close_prices)
        close_prices.columns = tickers
    
    # Clean missing values
    close_prices = close_prices.ffill()
    close_prices = close_prices.bfill()
    
    return close_prices


def calculate_statistics(prices, tickers):
    """
    Calculate key statistical metrics for each stock.
    """
    stats = pd.DataFrame()
    
    for ticker in tickers:
        if ticker in prices.columns:
            series = prices[ticker]
            stats[ticker] = {
                'Company': STOCKS.get(ticker, ticker),
                'Sector': SECTORS.get(ticker, 'N/A'),
                'Start Price ($)': series.iloc[0],
                'End Price ($)': series.iloc[-1],
                'Mean Price ($)': series.mean(),
                'Std Dev ($)': series.std(),
                'Min Price ($)': series.min(),
                'Max Price ($)': series.max(),
                'Total Return (%)': ((series.iloc[-1] / series.iloc[0]) - 1) * 100
            }
    
    return stats.T


def calculate_risk_metrics(returns, tickers):
    """
    Calculate risk metrics including volatility and Sharpe ratio.
    """
    risk_metrics = pd.DataFrame()
    
    RISK_FREE_RATE = 0.05 / 252
    
    for ticker in tickers:
        if ticker in returns.columns:
            series = returns[ticker]
            
            annual_vol = series.std() * np.sqrt(252)
            annual_return = series.mean() * 252
            sharpe = (annual_return - (RISK_FREE_RATE * 252 * 100)) / annual_vol if annual_vol > 0 else 0
            
            cumulative = (1 + series / 100).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max * 100
            max_drawdown = drawdown.min()
            
            risk_metrics[ticker] = {
                'Company': STOCKS.get(ticker, ticker),
                'Daily Volatility (%)': series.std(),
                'Annual Volatility (%)': annual_vol,
                'Annual Return (%)': annual_return,
                'Sharpe Ratio': sharpe,
                'Max Drawdown (%)': max_drawdown
            }
    
    return risk_metrics.T


def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Stock Performance Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Stock selection
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks to Analyze",
        options=list(STOCKS.keys()),
        default=['AAPL', 'MSFT', 'JPM'],
        format_func=lambda x: f"{x} - {STOCKS[x]}"
    )
    
    # Time period selection
    period_options = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730
    }
    
    selected_period = st.sidebar.selectbox(
        "Select Time Period",
        options=list(period_options.keys()),
        index=3
    )
    
    days = period_options[selected_period]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Analysis options
    st.sidebar.header("📊 Analysis Options")
    show_moving_avg = st.sidebar.checkbox("Show Moving Averages", value=True)
    ma_windows = st.sidebar.multiselect(
        "Moving Average Windows",
        options=[10, 20, 50, 100, 200],
        default=[20, 50],
        help="Select moving average periods to display"
    )
    
    show_bollinger = st.sidebar.checkbox("Show Bollinger Bands", value=False)
    
    # Main content
    if not selected_stocks:
        st.warning("⚠️ Please select at least one stock to analyze.")
        st.info("""
        **How to use this tool:**
        1. Select stocks from the sidebar
        2. Choose a time period
        3. Configure analysis options
        4. Explore the interactive charts and tables
        """)
        return
    
    # Data loading section
    with st.spinner("📥 Downloading stock data from Yahoo Finance..."):
        raw_data = download_stock_data(selected_stocks, start_date, end_date)
    
    if raw_data is None or raw_data.empty:
        st.warning("⚠️ Live data unavailable. Loading offline backup...")
        csv_path = os.path.join("data", "sample_stock_prices.csv")
        if os.path.exists(csv_path):
            backup = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            available = [t for t in selected_stocks if t in backup.columns]
            close_prices = backup[available].dropna()
            if close_prices.empty:
                st.error("❌ No matching stock data found in backup.")
                return
        else:
            st.error("❌ Offline backup file not found.")
            return
    else:
        close_prices = extract_close_prices(raw_data, selected_stocks)

    if close_prices is None or close_prices.empty:
        st.error("❌ No valid price data available.")
        return
    
    # Calculate daily returns
    daily_returns = close_prices.pct_change() * 100
    daily_returns = daily_returns.dropna()
    
    # Success message
    st.success(f"✅ Data loaded successfully! {len(close_prices)} trading days from {close_prices.index.min().strftime('%Y-%m-%d')} to {close_prices.index.max().strftime('%Y-%m-%d')}")
    
    # Key Metrics Dashboard
    st.header("📊 Key Metrics Dashboard")
    
    # Calculate statistics
    stats_df = calculate_statistics(close_prices, selected_stocks)
    risk_df = calculate_risk_metrics(daily_returns, selected_stocks)
    
    # Display metrics in columns
    cols = st.columns(min(len(selected_stocks), 4))
    
    for i, ticker in enumerate(selected_stocks[:4]):
        with cols[i]:
            if ticker in stats_df.index:
                return_val = stats_df.loc[ticker, 'Total Return (%)']
                delta_color = "normal" if return_val >= 0 else "inverse"
                st.metric(
                    label=f"{ticker}",
                    value=f"${stats_df.loc[ticker, 'End Price ($)']:.2f}",
                    delta=f"{return_val:.2f}%",
                    delta_color=delta_color
                )
                st.caption(f"{STOCKS.get(ticker, ticker)}")
    
    if len(selected_stocks) > 4:
        st.info(f"Showing metrics for first 4 of {len(selected_stocks)} selected stocks. See table below for all stocks.")
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Price Trends", 
        "📊 Statistics", 
        "⚠️ Risk Analysis", 
        "🔗 Correlation",
        "📋 Summary"
    ])
    
    # Tab 1: Price Trends
    with tab1:
        st.subheader("Stock Price Trends")
        
        # Normalized price chart
        st.write("**Normalized Performance (Base = 100)**")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        normalized = (close_prices / close_prices.iloc[0]) * 100
        
        for ticker in selected_stocks:
            if ticker in normalized.columns:
                ax.plot(normalized.index, normalized[ticker], label=ticker, linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Normalized Price')
        ax.set_title('Normalized Stock Performance')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close()
        
        # Individual stock with moving averages
        if show_moving_avg and ma_windows:
            st.write("**Individual Stock with Moving Averages**")
            
            selected_stock = st.selectbox(
                "Select stock for detailed view",
                options=selected_stocks,
                key="ma_stock_select"
            )
            
            if selected_stock in close_prices.columns:
                fig, ax = plt.subplots(figsize=(14, 7))
                
                ax.plot(close_prices.index, close_prices[selected_stock], 
                       label='Close Price', linewidth=2, color='black')
                
                colors = plt.cm.Set1(np.linspace(0, 1, len(ma_windows)))
                for window, color in zip(ma_windows, colors):
                    if len(close_prices) >= window:
                        ma = close_prices[selected_stock].rolling(window=window).mean()
                        ax.plot(close_prices.index, ma, 
                               label=f'{window}-day MA', linewidth=1.5, 
                               color=color, alpha=0.8)
                
                # Bollinger Bands
                if show_bollinger and len(close_prices) >= 20:
                    ma20 = close_prices[selected_stock].rolling(window=20).mean()
                    std20 = close_prices[selected_stock].rolling(window=20).std()
                    upper_band = ma20 + (std20 * 2)
                    lower_band = ma20 - (std20 * 2)
                    
                    ax.fill_between(close_prices.index, upper_band, lower_band, 
                                   alpha=0.2, color='gray', label='Bollinger Bands')
                
                ax.set_xlabel('Date')
                ax.set_ylabel('Price ($)')
                ax.set_title(f'{selected_stock} - Price and Technical Indicators')
                ax.legend(loc='upper left')
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                plt.close()
        
        # Total Returns Bar Chart
        st.write("**Total Returns Comparison**")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        returns = stats_df['Total Return (%)']
        colors = ['green' if x > 0 else 'red' for x in returns]
        
        bars = ax.bar(returns.index, returns, color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Ticker')
        ax.set_ylabel('Return (%)')
        ax.set_title('Total Return (%) - Selected Period')
        
        # Add value labels
        for bar, value in zip(bars, returns):
            height = bar.get_height()
            ax.annotate(f'{value:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
        
        st.pyplot(fig)
        plt.close()
    
    # Tab 2: Statistics
    with tab2:
        st.subheader("Descriptive Statistics")
        
        # Format and display statistics
        display_stats = stats_df.copy()
        display_stats = display_stats.round(2)
        
        st.dataframe(
            display_stats,
            width='stretch',
            height=400
        )
        
        # Download button
        csv = display_stats.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Statistics as CSV",
            data=csv,
            file_name="stock_statistics.csv",
            mime="text/csv"
        )
        
        # Price distribution
        st.write("**Price Distribution**")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        data_list = [close_prices[col].dropna().values for col in close_prices.columns]
        bp = ax.boxplot(data_list, labels=close_prices.columns, patch_artist=True)
        colors = plt.cm.Set3(range(len(close_prices.columns)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        ax.set_title('Stock Price Distribution')
        ax.set_xlabel('Ticker')
        ax.set_ylabel('Price ($)')
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
    
    # Tab 3: Risk Analysis
    with tab3:
        st.subheader("Risk Metrics Analysis")
        
        # Display risk metrics
        display_risk = risk_df.copy()
        display_risk = display_risk.round(4)
        
        st.dataframe(
            display_risk,
            width='stretch',
            height=400
        )
        
        # Risk-Return Scatter Plot
        st.write("**Risk-Return Profile**")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        annual_return = daily_returns.mean() * 252
        annual_vol = daily_returns.std() * np.sqrt(252)
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(selected_stocks)))
        
        for i, ticker in enumerate(selected_stocks):
            if ticker in daily_returns.columns:
                ax.scatter(annual_vol[ticker], annual_return[ticker], 
                          s=200, c=[colors[i]], label=ticker, 
                          edgecolors='black', linewidth=1.5)
                ax.annotate(ticker,
                           (annual_vol[ticker], annual_return[ticker]),
                           xytext=(10, 5), textcoords='offset points',
                           fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Annualized Volatility (%)')
        ax.set_ylabel('Annualized Return (%)')
        ax.set_title('Risk-Return Profile')
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close()
        
        # Volatility Comparison
        st.write("**Volatility Comparison**")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        volatility = daily_returns.std() * np.sqrt(252)
        bars = ax.bar(volatility.index, volatility, color='steelblue', 
                     alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Ticker')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.set_title('Annualized Volatility Comparison')
        
        st.pyplot(fig)
        plt.close()
    
    # Tab 4: Correlation
    with tab4:
        st.subheader("Correlation Analysis")
        
        if len(selected_stocks) >= 2:
            # Calculate correlation matrix
            corr_matrix = daily_returns.corr()
            
            # Display correlation matrix
            st.write("**Correlation Matrix of Daily Returns**")
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            sns.heatmap(corr_matrix,
                       mask=mask,
                       annot=True,
                       fmt='.3f',
                       cmap='RdYlGn',
                       center=0,
                       square=True,
                       linewidths=0.5,
                       cbar_kws={'shrink': 0.8},
                       ax=ax)
            
            ax.set_title('Stock Returns Correlation Matrix')
            
            st.pyplot(fig)
            plt.close()
            
            # Correlation insights
            st.write("**Correlation Insights**")
            
            # Find highest and lowest correlation pairs
            corr_values = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            
            if not corr_values.empty and not corr_values.isna().all().all():
                max_corr = corr_values.max().max()
                max_pair = corr_values.stack().idxmax()
                
                min_corr = corr_values.min().min()
                min_pair = corr_values.stack().idxmin()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📈 **Highest Correlation:** {max_pair[0]} & {max_pair[1]} = {max_corr:.4f}")
                    st.caption("These stocks tend to move together")
                
                with col2:
                    st.info(f"📉 **Lowest Correlation:** {min_pair[0]} & {min_pair[1]} = {min_corr:.4f}")
                    st.caption("These stocks are less correlated")
        else:
            st.warning("⚠️ Please select at least 2 stocks for correlation analysis.")
    
    # Tab 5: Summary
    with tab5:
        st.subheader("Analysis Summary")
        
        # Best and worst performers
        if len(selected_stocks) > 0 and not stats_df.empty:
            best_return = stats_df['Total Return (%)'].idxmax()
            worst_return = stats_df['Total Return (%)'].idxmin()
            
            safest = risk_df['Annual Volatility (%)'].idxmin()
            riskiest = risk_df['Annual Volatility (%)'].idxmax()
            
            best_sharpe = risk_df['Sharpe Ratio'].idxmax()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏆 Performance Highlights")
                st.write(f"**Best Performer:** {best_return}")
                st.write(f"- Return: {stats_df.loc[best_return, 'Total Return (%)']:.2f}%")
                st.write(f"- Company: {STOCKS.get(best_return, best_return)}")
                
                st.write(f"\n**Worst Performer:** {worst_return}")
                st.write(f"- Return: {stats_df.loc[worst_return, 'Total Return (%)']:.2f}%")
                st.write(f"- Company: {STOCKS.get(worst_return, worst_return)}")
            
            with col2:
                st.markdown("### ⚠️ Risk Analysis")
                st.write(f"**Lowest Volatility:** {safest}")
                st.write(f"- Annual Volatility: {risk_df.loc[safest, 'Annual Volatility (%)']:.2f}%")
                
                st.write(f"\n**Highest Volatility:** {riskiest}")
                st.write(f"- Annual Volatility: {risk_df.loc[riskiest, 'Annual Volatility (%)']:.2f}%")
                
                st.write(f"\n**Best Risk-Adjusted Return:** {best_sharpe}")
                st.write(f"- Sharpe Ratio: {risk_df.loc[best_sharpe, 'Sharpe Ratio']:.4f}")
            
            # Investment insights
            st.markdown("---")
            st.markdown("### 💡 Investment Insights")
            
            insights = []
            
            # Performance insight
            if stats_df['Total Return (%)'].mean() > 0:
                insights.append("📈 The selected stocks show positive average returns over the period.")
            else:
                insights.append("📉 The selected stocks show negative average returns over the period.")
            
            # Risk insight
            avg_vol = risk_df['Annual Volatility (%)'].mean()
            if avg_vol > 30:
                insights.append("⚠️ High average volatility suggests significant price fluctuations.")
            elif avg_vol > 20:
                insights.append("📊 Moderate volatility indicates balanced risk-return profile.")
            else:
                insights.append("✅ Low volatility suggests stable price movements.")
            
            # Sharpe ratio insight
            avg_sharpe = risk_df['Sharpe Ratio'].mean()
            if avg_sharpe > 1:
                insights.append("🎯 Strong risk-adjusted returns across selected stocks.")
            elif avg_sharpe > 0:
                insights.append("📊 Positive but moderate risk-adjusted returns.")
            else:
                insights.append("⚠️ Negative risk-adjusted returns suggest caution.")
            
            for insight in insights:
                st.write(insight)
        
        # Data source info
        st.markdown("---")
        st.markdown("### 📋 Data Information")
        st.write(f"**Data Source:** Yahoo Finance (via yfinance library)")
        st.write(f"**Analysis Period:** {selected_period}")
        st.write(f"**Date Range:** {close_prices.index.min().strftime('%Y-%m-%d')} to {close_prices.index.max().strftime('%Y-%m-%d')}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        <p>Stock Performance Analyzer | ACC102 Mini Assignment - Track 4</p>
        <p>Data provided by Yahoo Finance. For educational purposes only.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()