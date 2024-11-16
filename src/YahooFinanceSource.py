import os
import pandas as pd
import yfinance as yf


class YahooFinanceSource:

    def __init__(self, ticker, REPO_PATH):
        self.ticker = ticker
        self.yf_dir = os.path.join(REPO_PATH, "data/yfinance/")
        if not os.path.exists(self.yf_dir):
            os.makedirs(self.yf_dir)
        self.file_path = os.path.join(self.yf_dir, f"{self.ticker}.csv")

    def fetch_ticker(self):
        data = pd.DataFrame()

        # Check if already have data in local
        if os.path.exists(self.file_path):
            # data = self._update_existing_data()
            # TODO: Debug
            data = self._download_new_data()
        else:
            data = self._download_new_data()

        return data

    def _download_new_data(self):
        print(f"Download new {self.ticker} data.")
        new_data = yf.download(
            self.ticker,
            end=pd.Timestamp.today(),
            progress=False,
            multi_level_index=False,
        )
        new_data.reset_index(inplace=True)
        new_data['Ticker'] = self.ticker
        # save to local
        new_data.to_csv(self.file_path, index=False)
        return new_data

    def _update_existing_data(self):
        # TODO: Debug
        print("--------------------")
        print(f"Update {self.ticker} data.")
        old_data = pd.read_csv(self.file_path, index_col="Date", parse_dates=True)
        latest_local_date = old_data.index.max()

        # Download new data [latest_local_date+1,today)
        new_data = yf.download(
            self.ticker,
            start=latest_local_date + pd.DateOffset(1),
            end=pd.Timestamp.today().normalize(),
            progress=False,
            multi_level_index=False,
        )
        if new_data.empty:
            print(f"No new data for {self.ticker}.")
            return old_data

        # Merge old and new data
        updated_data = pd.concat([old_data, new_data])
        # Remove duplicate dates
        updated_data = updated_data[~updated_data.index.duplicated(keep="last")]
        # save to local
        updated_data.to_csv(self.file_path, index=False)
        return updated_data
