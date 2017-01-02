import abc
import logging

import pyalgotrade.broker
from pyalgotrade.cn.broker import backtesting
from pyalgotrade.strategy import BaseStrategy


class BacktestingStrategy(BaseStrategy):
    """Base class for backtesting strategies.

    :param barFeed: The bar feed to use to backtest the strategy.
    :type barFeed: :class:`pyalgotrade.barfeed.BaseBarFeed`.
    :param cash_or_brk: The starting capital or a broker instance.
    :type cash_or_brk: int/float or :class:`pyalgotrade.broker.Broker`.

    .. note::
        This is a base class and should not be used directly.
    """

    def __init__(self, barFeed, cash_or_brk=1000000):
        # The broker should subscribe to barFeed events before the strategy.
        # This is to avoid executing orders submitted in the current tick.

        if isinstance(cash_or_brk, pyalgotrade.broker.Broker):
            broker = cash_or_brk
        else:
            broker = backtesting.Broker(cash_or_brk, barFeed)

        BaseStrategy.__init__(self, barFeed, broker)
        self.__useAdjustedValues = False
        self.setUseEventDateTimeInLogs(True)
        self.setDebugMode(True)

    def getUseAdjustedValues(self):
        return self.__useAdjustedValues

    def setUseAdjustedValues(self, useAdjusted):
        self.getFeed().setUseAdjustedValues(useAdjusted)
        self.getBroker().setUseAdjustedValues(useAdjusted)
        self.__useAdjustedValues = useAdjusted

    def setDebugMode(self, debugOn):
        """Enable/disable debug level messages in the strategy and backtesting broker.
        This is enabled by default."""
        level = logging.DEBUG if debugOn else logging.INFO
        self.getLogger().setLevel(level)
        self.getBroker().getLogger().setLevel(level)
