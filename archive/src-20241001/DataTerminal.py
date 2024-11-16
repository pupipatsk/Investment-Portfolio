import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.data_sources import YahooFinanceSource
from src.logging_utils import setup_logger

class DataTerminal:
    """Orchestrates data fetching from various financial data sources."""

    def __init__(self, REPO_PATH=os.path.abspath(os.path.join(".."))):
        """Initializes the DataTerminal object.

        Args:
            REPO_PATH (str): The path to the repository. Defaults to the parent directory of the current working directory.
        """
        self.TODAY = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        self.YESTERDAY = self.TODAY - pd.DateOffset(1)

        self.REPO_PATH = REPO_PATH
        self.YF_PATH = os.path.join(self.REPO_PATH, "data/yfinance/")
        if not os.path.exists(self.YF_PATH):
            os.makedirs(self.YF_PATH)

        # Set up logging
        self.logger = setup_logger(self.REPO_PATH, "yfinance")

        # Initialize data source
        self.YahooFinanceSource = YahooFinanceSource(
            self.YF_PATH, self.TODAY, self.YESTERDAY, self.logger
        )

    def fetch_yfinance(self, tickers, max_workers=5):
        """Fetches yfinance data for the given tickers concurrently.

        Args:
            tickers (list): A list of ticker symbols.
            max_workers (int): The maximum number of threads to use for fetching data concurrently.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched yfinance data with columns ['Date', 'Ticker', 'Adj Close'].
        """
        df_return = pd.DataFrame()

        # Fetch data concurrently for each ticker using YahooFinanceSource
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    # Call Fetch function
                    self.YahooFinanceSource.fetch_ticker_data, ticker
                ): ticker
                for ticker in sorted(tickers)
            }
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    data = future.result()
                    df_return = pd.concat([df_return, data])
                except Exception as e:
                    self.logger.error(f"Error fetching data for {ticker}: {str(e)}")

        df_return.reset_index(inplace=True)
        features = ["Date", "Ticker", "Adj Close"]
        return df_return[features]
