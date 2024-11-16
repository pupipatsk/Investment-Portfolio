import os
import pandas as pd
import yfinance as yf
from .DataSource import DataSource


class YahooFinanceSource(DataSource):
    """Fetches data from Yahoo Finance."""

    def __init__(self, data_path, today, yesterday, logger):
        """Initializes the YahooFinanceSource.

        Args:
            data_path (str): Path to store data files.
            today (pd.Timestamp): Today's date.
            yesterday (pd.Timestamp): Yesterday's date.
            logger (logging.Logger): Logger instance for logging events.
        """
        self.data_path = data_path
        self.today = today
        self.yesterday = yesterday
        self.logger = logger

    def fetch_ticker_data(self, ticker):
        """Fetches data for a single ticker.

        Args:
            ticker (str): The ticker symbol.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched yfinance data for the ticker.
        """
        self.logger.info(f"Processing ticker: {ticker}")
        file_path = os.path.join(self.data_path, f"{ticker}.csv")
        data = pd.DataFrame()

        # Check if local data exists
        if os.path.exists(file_path):
            data = self._update_existing_data(file_path, ticker)
        else:
            data = self._fetch_full_history(ticker)

        data["Ticker"] = ticker
        return data

    def _update_existing_data(self, file_path, ticker):
        """Updates existing data for a ticker by fetching new data.

        Args:
            file_path (str): Path to the existing data file.
            ticker (str): The ticker symbol.

        Returns:
            pd.DataFrame: The updated data.
        """
        old_data = pd.read_csv(file_path, index_col="Date", parse_dates=True)
        latest_date = pd.to_datetime(old_data.index.max())
        self.logger.info(f"Latest date in local: {latest_date.strftime('%Y-%m-%d')}")

        if latest_date < self.yesterday:
            start_date = (latest_date + pd.DateOffset(1)).strftime("%Y-%m-%d")
            end_date = self.today.strftime("%Y-%m-%d")
            try:
                new_data = self.fetch_data(ticker, start=start_date, end=end_date)
                self.logger.info(f"Downloaded new data [{start_date}, {end_date})")

                if not new_data.empty and new_data.index[0] > latest_date:
                    updated_data = pd.concat([old_data, new_data])
                    updated_data.to_csv(file_path)
                    return updated_data
                else:
                    self.logger.info("Already up-to-date.")
                    return old_data
            except Exception as e:
                self.logger.error(f"Failed to download new data for {ticker}: {str(e)}")
                return old_data
        else:
            self.logger.info("Already up-to-date.")
            return old_data

    def _fetch_full_history(self, ticker):
        """Fetches full historical data for a ticker.

        Args:
            ticker (str): The ticker symbol.

        Returns:
            pd.DataFrame: The full historical data.
        """
        try:
            data = self.fetch_data(ticker, end=self.today.strftime("%Y-%m-%d"))
            if not data.empty:
                file_path = os.path.join(self.data_path, f"{ticker}.csv")
                data.to_csv(file_path)
                self.logger.info(f"Downloaded all historical data for {ticker}.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to download historical data for {ticker}: {str(e)}")
            return pd.DataFrame()

    def fetch_data(self, ticker, start=None, end=None):
        """Fetches historical data for a given ticker from Yahoo Finance.

        Args:
            ticker (str): The ticker symbol.
            start (str, optional): The start date for the data. Defaults to None.
            end (str, optional): The end date for the data. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the historical data.
        """
        try:
            data = yf.download(ticker, start=start, end=end)
            return data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Yahoo Finance: {e}")
