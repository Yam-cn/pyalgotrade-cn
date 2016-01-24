# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import stratanalyzer
from pyalgotrade import broker

import numpy as np
import datetime as dt
import uuid

class Pusher(stratanalyzer.StrategyAnalyzer):
    """A :class:`pyalgotrade.stratanalyzer.StrategyAnalyzer` that records the profit/loss
    and returns of every completed trade.

    .. note::
        This analyzer operates on individual completed trades.
        For example, lets say you start with a $1000 cash, and then you buy 1 share of XYZ
        for $10 and later sell it for $20:

            * The trade's profit was $10.
            * The trade's return is 100%, even though your whole portfolio went from $1000 to $1020, a 2% return.
    """

    def __init__(self, figure_id, strategy_id):
        self.__figure_id = figure_id
        self.__strategy_id = strategy_id


    def __onOrderEvent(self, broker_, orderEvent):
        # Only interested in accepted
        if orderEvent.getEventType() not in (broker.OrderEvent.Type.PARTIALLY_FILLED, broker.OrderEvent.Type.FILLED):
            return

        order = orderEvent.getOrder()
        

        # Update the tracker for this order.
        execInfo = orderEvent.getEventInfo()
        price = execInfo.getPrice()
        action = order.getAction()
        if action in [broker.Order.Action.BUY, broker.Order.Action.BUY_TO_COVER]:
            quantity = execInfo.getQuantity()
        elif action in [broker.Order.Action.SELL, broker.Order.Action.SELL_SHORT]:
            quantity = execInfo.getQuantity() * -1
        else:  # Unknown action
            assert(False)
        
        instrument_id = order.getInstrument()
        
        order_id = uuid.uuid1()
        
        message = [execInfo.getDateTime(), self.__figure_id, self.__strategy_id, instrument_id, action, order_id, price, quantity]
        
        print message
        

    def attached(self, strat):
        strat.getBroker().getOrderUpdatedEvent().subscribe(self.__onOrderEvent)

    def getCount(self):
        """Returns the total number of trades."""
        return len(self.__all)

    def getProfitableCount(self):
        """Returns the number of profitable trades."""
        return len(self.__profits)

    def getUnprofitableCount(self):
        """Returns the number of unprofitable trades."""
        return len(self.__losses)

    def getEvenCount(self):
        """Returns the number of trades whose net profit was 0."""
        return self.__evenTrades

    def getAll(self):
        """Returns a numpy.array with the profits/losses for each trade."""
        return np.asarray(self.__all)

    def getProfits(self):
        """Returns a numpy.array with the profits for each profitable trade."""
        return np.asarray(self.__profits)

    def getLosses(self):
        """Returns a numpy.array with the losses for each unprofitable trade."""
        return np.asarray(self.__losses)

    def getAllReturns(self):
        """Returns a numpy.array with the returns for each trade."""
        return np.asarray(self.__allReturns)

    def getPositiveReturns(self):
        """Returns a numpy.array with the positive returns for each trade."""
        return np.asarray(self.__positiveReturns)

    def getNegativeReturns(self):
        """Returns a numpy.array with the negative returns for each trade."""
        return np.asarray(self.__negativeReturns)

    def getCommissionsForAllTrades(self):
        """Returns a numpy.array with the commissions for each trade."""
        return np.asarray(self.__allCommissions)

    def getCommissionsForProfitableTrades(self):
        """Returns a numpy.array with the commissions for each profitable trade."""
        return np.asarray(self.__profitableCommissions)

    def getCommissionsForUnprofitableTrades(self):
        """Returns a numpy.array with the commissions for each unprofitable trade."""
        return np.asarray(self.__unprofitableCommissions)

    def getCommissionsForEvenTrades(self):
        """Returns a numpy.array with the commissions for each trade whose net profit was 0."""
        return np.asarray(self.__evenCommissions)
