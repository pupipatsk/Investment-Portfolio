import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# --- System and Path --- #
REPO_PATH = os.path.abspath(os.path.join('..'))
if REPO_PATH not in sys.path:
    sys.path.append(REPO_PATH)

# Load Data Function
def load_data():
    df_portfolio = pd.read_csv(
        REPO_PATH + '/data/private/csv/20241110-Portfolio.csv',
        parse_dates=['Date']
    )
    df_portfolio_metrics = pd.read_csv(
        REPO_PATH + '/data/private/csv/20241110-PortfolioMetrics.csv',
        parse_dates=['Date'],
        index_col='Date'
    )
    return df_portfolio, df_portfolio_metrics

df_portfolio, df_portfolio_metrics = load_data()

# Title
st.title("Investment Portfolio Dashboard")
# Display the latest data date
latest_date = df_portfolio['Date'].max()
st.write(f"Latest Data Date: {latest_date.date()}")
st.write("(The financial data is no longer being updated for confidentiality reasons.)")

st.header("Portfolio Return")
st.write(f"First Investment Date: {df_portfolio['Date'].min().date()}")

# Percent Metrics
usd_metrics = {
    "Unrealized PnL": df_portfolio_metrics["Portfolio Unrealized PnL (%)"].iloc[-1],
    "Return on Interest (ROI)": df_portfolio_metrics["ROI (%)"].iloc[-1],
}

max_cols = 3
num_metrics = len(usd_metrics)
num_cols = min(num_metrics, max_cols)
cols = st.columns(num_cols)

# Distribute metrics across the columns with conditional colors
for i, metric in enumerate(usd_metrics):
    value = usd_metrics[metric]
    color = "rgba(0, 220, 0, 1.0)" if value >= 0 else "rgba(225, 0, 0, 1.0)"  # Set color based on the value

    # Using HTML in st.markdown for conditional color formatting
    with cols[i % num_cols]:  # Wrap around columns
        st.markdown(
            f"<div style='text-align: center;'>"
            f"<strong>{metric}</strong><br>"
            f"<span style='color: {color}; font-size: 2em;'>{value:.2f} %</span>"
            f"</div>",
            unsafe_allow_html=True
        )


# Portfolio Return
def plot_portfolio_return(df_metrics, y1, y2):
    fig = go.Figure()

    # Portfolio Unrealized PnL (%) trace
    color1 = "rgba(255, 0, 0, 1.0)" if df_metrics[y1].iloc[-1] < 0 else "rgba(0, 255, 0, 1.0)"
    fig.add_trace(
        go.Scatter(
            x=df_metrics.index,
            y=df_metrics[y1],
            mode="lines",
            name=y1,
            line=dict(color=color1),
        )
    )

    # Portfolio Cumulative Return (%) trace
    color2 = "rgba(126, 0, 0, 0.5)" if df_metrics[y2].iloc[-1] < 0 else "rgba(0, 126, 0, 0.5)"
    fig.add_trace(
        go.Scatter(
            x=df_metrics.index,
            y=df_metrics[y2],
            mode="lines",
            name=y2,
            fill="tozeroy",
            fillcolor=color2,
            line=dict(color=color2),
        )
    )

    fig.update_layout(
        title="Portfolio Return (%)",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        template="plotly_dark",
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Plot Portfolio Metrics
plot_portfolio_return(
    df_portfolio_metrics,
    y1="Portfolio Unrealized PnL (%)",
    y2="ROI (%)"
)


# THB Metrics (convert to THB)
# Exchange Rate
exchange_rate = 34.275
thb_metrics = {
    "Portfolio Value (THB)": df_portfolio_metrics["Portfolio Value (USD)"].iloc[-1] * exchange_rate,
    "Cumulative Deposit (THB)": df_portfolio_metrics["Cumulative Deposit (USD)"].iloc[-1] * exchange_rate,
    "Unrealized PnL (THB)": df_portfolio_metrics["Portfolio Unrealized PnL (USD)"].iloc[-1] * exchange_rate,
    "Net Profit (THB)": df_portfolio_metrics["Portfolio Net Profit (USD)"].iloc[-1] * exchange_rate,
}

# Display THB Metrics in 4 columns
cols_thb = st.columns(2)
for i, (metric, value) in enumerate(thb_metrics.items()):
    with cols_thb[i % 2]:
        st.metric(label=metric, value=f"฿ {value:,.2f}")

st.write("2024-11-10 Exchange Rate: 34.275 THB / 1 USD")


# Display Additional Portfolio Metrics
st.subheader("Perfomance Metrics")

# Define available metrics
available_metrics = {
    "Sharpe Ratio": df_portfolio_metrics["Dynamic Sharpe Ratio"].iloc[-1],
    "Sortino Ratio": df_portfolio_metrics["Dynamic Sortino Ratio"].iloc[-1],
    "Volatility 30d (%)": df_portfolio_metrics["Volatility_30d (%)"].iloc[-1],
    "CVaR 95%": df_portfolio_metrics["CVaR 95%"].iloc[-1],
    "Mean Return (%)": df_portfolio_metrics["Mean return (%)"].iloc[-1],
    "Std Return (%)": df_portfolio_metrics["Std return (%)"].iloc[-1],
}

# Multi-select widget for users to select metrics
selected_metrics = st.multiselect(
    "Select metrics to display:",
    options=list(available_metrics.keys()),
    default=list(available_metrics.keys())  # Default to showing all metrics
)

# Display selected metrics with a maximum of 4 columns
max_cols = 4
num_metrics = len(selected_metrics)
num_cols = min(num_metrics, max_cols)
cols = st.columns(num_cols)  # Create up to 4 columns

# Distribute metrics across the columns, wrapping if more than 4 metrics
for i, metric in enumerate(selected_metrics):
    with cols[i % num_cols]:  # Wrap around columns if more than 4 metrics
        st.metric(label=metric, value=f"{available_metrics[metric]:.2f}")


st.header("Portfolio Composition")

# Treemap plotting function for the latest date
def plot_latest_treemap(df, path_column="Ticker", value_column="Asset Value (USD)", color_column="Asset Unrealized PnL (%)"):
    latest_date = df['Date'].max()
    latest_df = df[df['Date'] == latest_date]
    latest_df = latest_df.dropna(subset=[path_column, value_column, color_column])
    latest_df = latest_df[latest_df[value_column] > 0]

    if latest_df.empty:
        st.warning(f"No data available for {value_column} on the latest date ({latest_date.date()}).")
        return

    color_scale = [(0, "rgb(223,72,76)"), # Red
                   (0.4, "rgb(118,45,48)"),
                   (0.5, "rgb(55,58,68)"),
                   (0.6, "rgb(32,50,39)"),
                   (1, "rgb(68,190,87)")]  # Green

    # Create the treemap figure, displaying `Ticker` and `Asset Unrealized PnL (%)` in the center of each block
    fig = px.treemap(
        latest_df,
        path=[path_column],
        values=value_column,
        color=color_column,
        color_continuous_scale=color_scale,
        title=f"Treemap of {value_column} by {path_column} on {latest_date.date()}",
        hover_data={color_column: ':.2f'},  # Format to show two decimal points on hover
        custom_data=[path_column, color_column]  # For displaying custom text in each block
    )

    # Display `Ticker` and `Asset Unrealized PnL (%)` in the center of each block
    fig.update_traces(
        texttemplate='%{customdata[0]}<br>%{customdata[1]:.2f}%',  # Show Ticker and Asset Unrealized PnL (%)
        textposition='middle center'
    )

    # Set color axis midpoint to zero to differentiate positive/negative values
    fig.update_coloraxes(cmid=0)

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Plotting the treemap with `Asset Value (USD)` as the size and `Asset Unrealized PnL (%)` as the color
plot_latest_treemap(
    df_portfolio,
    path_column="Ticker",
    value_column="Asset Value (USD)",
    color_column="Asset Unrealized PnL (%)"
)



# USD Metrics
usd_metrics = {
    "Portfolio Value (USD)": df_portfolio_metrics["Portfolio Value (USD)"].iloc[-1],
    "Cumulative Deposit (USD)": df_portfolio_metrics["Cumulative Deposit (USD)"].iloc[-1],
    "Cash (USD)": df_portfolio_metrics["Cash"].iloc[-1],
    "Unrealized PnL (USD)": df_portfolio_metrics["Portfolio Unrealized PnL (USD)"].iloc[-1],
    "Net Profit (USD)": df_portfolio_metrics["Portfolio Net Profit (USD)"].iloc[-1],
}

max_cols = 3
num_metrics = len(usd_metrics)
num_cols = min(num_metrics, max_cols)
cols = st.columns(num_cols)

# Display USD Metrics
for i, metric in enumerate(usd_metrics):
    with cols[i % num_cols]:  # Wrap around columns
        st.metric(label=metric, value=f"$ {usd_metrics[metric]:,.2f}")


def plot_portfolio_usd(df):
    """
    Plots Portfolio Value, Cumulative Deposit, and Cash as lines, and Unrealized PnL & Net Profit as stacked bars.

    Args:
        df (DataFrame): The DataFrame containing the portfolio metrics with Date as index.
    """
    # Create the figure
    fig = go.Figure()

    # Add Portfolio Value (USD) line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Portfolio Value (USD)"],
        mode="lines",
        name="Portfolio Value (USD)",
        line=dict(color="skyblue")
    ))

    # Add Cumulative Deposit (USD) line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Cumulative Deposit (USD)"],
        mode="lines",
        name="Cumulative Deposit (USD)",
        line=dict(color="orange", dash="dot")
    ))

    # Add Cash line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Cash"],
        mode="lines",
        name="Cash",
        line=dict(color="lightgrey", dash="dash")
    ))

    # Add Unrealized PnL (USD) stacked bar
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Portfolio Unrealized PnL (USD)"],
        name="Unrealized PnL (USD)",
        marker=dict(color="green")
    ))

    # Add Net Profit (USD) stacked bar
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Portfolio Net Profit (USD)"],
        name="Net Profit (USD)",
        marker=dict(color="rgb(0,255,0)")
    ))

    # Update layout for stacked bar and line chart
    fig.update_layout(
        title="Portfolio USD",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        template="plotly_dark",
        barmode="relative",  # Stacks the bars on top of each other
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Use the function to plot the graph
plot_portfolio_usd(df_portfolio_metrics)


st.subheader("Asset Graphs")

def plot_asset_line_graph(df, default_value_column="Market Price (USD)"):
    """
    Plots a line graph for selected tickers and columns in the portfolio.

    Args:
        df (DataFrame): The DataFrame containing portfolio data.
        default_value_column (str): The default column to plot if no other column is selected.
    """
    # Get unique tickers for filtering
    tickers = df["Ticker"].unique()

    # Multi-select widget for filtering tickers
    selected_tickers = st.multiselect(
        "Select assets (Tickers) to display:",
        options=tickers,
        default=tickers[:3] if len(tickers) > 3 else tickers  # Show up to 3 tickers by default
    )

    # Multi-select widget for selecting columns to display
    available_columns = ["Average Cost Price (USD)",
                         "Cumulative Volume",
                         "Market Price (USD)",
                         "Asset Value (USD)",
                         "Asset Unrealized PnL (USD)",
                         "Asset Unrealized PnL (%)"]
    selected_columns = st.multiselect(
        "Select features to display:",
        options=available_columns,
        default=[default_value_column]
    )

    # Filter DataFrame for selected tickers
    filtered_df = df[df["Ticker"].isin(selected_tickers)]

    # Define colors and line styles
    colors = px.colors.qualitative.Plotly  # Get a set of colors from Plotly's palette
    dash_styles = ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]  # Different line styles

    # Map each ticker to a unique color
    ticker_colors = {ticker: colors[i % len(colors)] for i, ticker in enumerate(selected_tickers)}

    # Create a line plot for each selected ticker and column combination
    fig = go.Figure()

    for ticker in selected_tickers:
        ticker_df = filtered_df[filtered_df["Ticker"] == ticker]

        for i, column in enumerate(selected_columns):
            fig.add_trace(
                go.Scatter(
                    x=ticker_df["Date"],
                    y=ticker_df[column],
                    mode="lines",
                    name=f"{ticker} - {column}",
                    line=dict(color=ticker_colors[ticker], dash=dash_styles[i % len(dash_styles)])
                )
            )

    # Update the layout for the line chart
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_dark",
        height=600,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Use the function to plot the graph
plot_asset_line_graph(df_portfolio)



# Stacked Bar Chart Plotting Function
def plot_stacked_bar_chart(df, x_column, value_column, category_column):
    df = df.sort_values(by=x_column)
    fig = go.Figure()

    for category in df[category_column].unique():
        category_df = df[df[category_column] == category]
        fig.add_trace(go.Bar(
            x=category_df[x_column],
            y=category_df[value_column],
            name=category
        ))

    fig.update_layout(
        barmode='stack',
        title=f"Stacked Bar Chart of {value_column} by {category_column}",
        xaxis_title=x_column,
        yaxis_title=value_column,
        template="plotly_dark",
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)

# Plotting the stacked bar chart with Asset Value (USD) as the bar size
plot_stacked_bar_chart(
    df_portfolio,
    x_column="Date",
    value_column="Asset Value (USD)",
    category_column="Ticker"
)
