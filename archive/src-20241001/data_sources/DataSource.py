from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def fetch_data(self, tickers):
        pass
