import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def load_data():
    filepath = '/Users/pupipatsingkhorn/Developer/repositories/Investment-Portfolio/data/private/csv/20241110-PortfolioMetric.csv'
    df = pd.read_csv(filepath, parse_dates=True, index_col='Date')
    return df

df = load_data()

# Title
st.title("Investment Portfolio Analysis Dashboard")

# Display dataset information
st.header("Dataset Overview")
st.write("Data snapshot:")
st.write(df.head())

# Display summary statistics
st.write("Summary statistics:")
st.write(df.describe())

# Filter options
st.sidebar.header("Filters")
ticker_options = df['Ticker'].unique()
selected_tickers = st.sidebar.multiselect("Select Tickers:", ticker_options, default=ticker_options)
date_range = st.sidebar.date_input("Select Date Range:", [df.index.min(), df.index.max()])

# Filter data based on user selection
filtered_df = df[(df['Ticker'].isin(selected_tickers)) & (df.index >= pd.to_datetime(date_range[0])) & (df.index <= pd.to_datetime(date_range[1]))]

# Key metrics to display
st.header("Portfolio and Market Metrics")
st.subheader("Portfolio Value (USD)")
fig1, ax1 = plt.subplots()
ax1.plot(filtered_df.index, filtered_df['Portfolio Value (USD)'], label='Portfolio Value (USD)')
ax1.set_xlabel("Date")
ax1.set_ylabel("Portfolio Value (USD)")
ax1.legend()
st.pyplot(fig1)

st.subheader("Market Price (USD) by Ticker")
for ticker in selected_tickers:
    fig, ax = plt.subplots()
    ticker_df = filtered_df[filtered_df['Ticker'] == ticker]
    ax.plot(ticker_df.index, ticker_df['Market Price (USD)'], label=f'Market Price (USD) - {ticker}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Market Price (USD)")
    ax.legend()
    st.pyplot(fig)

# Portfolio Cumulative Return and PnL
st.header("Cumulative Returns and PnL")
fig2, ax2 = plt.subplots()
ax2.plot(filtered_df.index, filtered_df['Portfolio Cumulative Return (USD)'], label='Cumulative Return (USD)')
ax2.set_xlabel("Date")
ax2.set_ylabel("Portfolio Cumulative Return (USD)")
ax2.legend()
st.pyplot(fig2)

fig3, ax3 = plt.subplots()
ax3.plot(filtered_df.index, filtered_df['Portfolio Unrealized PnL (USD)'], label='Unrealized PnL (USD)')
ax3.set_xlabel("Date")
ax3.set_ylabel("Unrealized PnL (USD)")
ax3.legend()
st.pyplot(fig3)

# Display insights
st.header("Insights")
st.write("### Ticker-wise Summary")
for ticker in selected_tickers:
    ticker_df = filtered_df[filtered_df['Ticker'] == ticker]
    st.write(f"#### {ticker}")
    st.write(ticker_df[['Average Cost Price (USD)', 'Market Price (USD)', 'Asset Unrealized PnL (%)']].describe())

st.write("### Portfolio Overview")
st.write(f"Total Portfolio Value on {filtered_df.index[-1].date()}: ${filtered_df['Portfolio Value (USD)'].iloc[-1]:,.2f}")
st.write(f"Total Unrealized PnL: ${filtered_df['Portfolio Unrealized PnL (USD)'].iloc[-1]:,.2f}")
st.write(f"Total Cumulative Return (%): {filtered_df['Portfolio Cumulative Return (%)'].iloc[-1]:.2f}%")
