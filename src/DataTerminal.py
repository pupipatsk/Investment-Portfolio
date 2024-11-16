import os
import pandas as pd
from src.YahooFinanceSource import *

class DataTerminal:

    def __init__(self, REPO_PATH=os.path.abspath(os.path.join(".."))):
        self.REPO_PATH = REPO_PATH

    def fetch_data(self, tickers):
        df_return = pd.DataFrame()

        for ticker in sorted(tickers):
            data = YahooFinanceSource(ticker=ticker, REPO_PATH=self.REPO_PATH).fetch_ticker()

            df_return = pd.concat([df_return, data], axis=0)

        # Normalize date
        df_return['Date'] = pd.to_datetime(df_return['Date'], utc=True)
        df_return['Date'] = df_return['Date'].dt.date.astype('datetime64[ns]')

        return df_return
