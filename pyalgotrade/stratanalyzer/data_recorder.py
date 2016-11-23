# encoding: utf-8
"""For data analyse purpose, we may want the whole history data. Here we utilize pd as the container."""

from pyalgotrade import stratanalyzer
import pandas as pd

class HistBarsRecorder(stratanalyzer.StrategyAnalyzer):
    """This class is used to contain the history data."""
    def __init__(self):
        self.__bar_dataframe = pd.DataFrame(columns=['Stock_id', 'Open', 'Low', 'High', 'Close', 'AdjClose'])

    def beforeAttach(self, strat):
        pass

    def attached(self, strat):
        pass

    def beforeOnBars(self, strat, bars):
        # We only record the data
        self.__today = pd.Timestamp(bars.getDateTime())
        for stock_id, bar in bars.items():
            self.__bar_dataframe.loc[self.__today] = [stock_id, bar.getOpen(), bar.getLow(), bar.getHigh(), bar.getClose(), bar.getAdjClose()]

    def get_history_bars(self):
        """In case of the risk of future data, we only have access to history data till yesterday. Current bars is not avaible."""
        return self.__bar_dataframe.iloc[:-1]
        