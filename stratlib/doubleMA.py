# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 13:06:56 2015

@author: Eunice
"""

if __name__ == '__main__':
    import sys
    sys.path.append("..")     
    from pyalgotrade import bar
    from pyalgotrade import plotter
# 以上模块仅测试用
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross

class DoubleMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, n, m):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__malength1 = int(n)
        self.__malength2 = int(m)
        
        self.__ma1 = ma.SMA(self.__prices, self.__malength1)
        self.__ma2 = ma.SMA(self.__prices, self.__malength2)
        
    def getPrice(self):
        return self.__prices

    def getSMA(self):
        return self.__ma1,self.__ma2

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None
        #self.info("long close")

    def onExitCanceled(self, position):
        self.__position.exitMarket()            

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        
        if self.__ma2[-1]is None:
            return 
            
        if self.__position is not None:
            if not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0:
                self.__position.exitMarket()
                #self.info("sell %s" % (bars.getDateTime()))
        
        if self.__position is None:
            if cross.cross_above(self.__ma1, self.__ma2) > 0:
                shares = int(self.getBroker().getEquity() * 0.2 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares)
                print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
                #self.info("buy %s" % (bars.getDateTime()))
    
    
if __name__ == "__main__": 
    strat = DoubleMA    
    instrument = '000001'
    market = 'SZ'
    fromDate = '20140101'
    toDate ='20160101'
    frequency = bar.Frequency.DAY
    paras = [5, 20]
    plot = True
    
    #############################################path set ############################33 
    if frequency == bar.Frequency.MINUTE:
        path = "..\\histdata\\min\\"
    elif frequency == bar.Frequency.DAY:
        path = "..\\histdata\\day\\"
    filepath = path + instrument + market + ".csv"
    
    
    #############################################don't change ############################33  
    from pyalgotrade.barfeed.csvfeed import GenericBarFeed

    
    barfeed = GenericBarFeed(frequency)
    barfeed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')
    barfeed.addBarsFromCSV(instrument, filepath)
    strat = strat(barfeed, instrument, *paras)
    
    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        
    strat.run()
    
    if plot:
        plt.plot()
        































