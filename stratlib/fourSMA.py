# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 13:06:56 2015

@author: Eunice
"""

if __name__ == '__main__':
    import sys
    sys.path.append("..")     
    from pyalgotrade import plotter
# 以上模块仅测试用
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade import bar
from pyalgotrade.dataseries import SequenceDataSeries


class fourSMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, mall, mals, masl, mass):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__instrument = instrument
        self.__close = feed[instrument].getCloseDataSeries()
        self.__longPos = None
        self.__shortPos = None
        self.__mall = ma.SMA(self.__close, int(mall))
        self.__mals = ma.SMA(self.__close, int(mals))
        self.__masl = ma.SMA(self.__close, int(masl))
        self.__mass = ma.SMA(self.__close, int(mass))
        
        self.__position = SequenceDataSeries()
        
    def getPrice(self):
        return self.__prices

    def getSMA(self):
        return self.__mall,self.__mals,self.__mass,self.__masl

    def testCon(self):
        
        # record position      
        #######################################################################
        if self.__longPos is not None:
            self.__position.append(1)
        if self.__shortPos is not None:
            self.__position.append(-1)
        elif self.__longPos is None and self.__shortPos is None:
            self.__position.append(0)
        
        
    def getTest(self):
        return self.__position
    
    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitCanceled(self, position):
        position.exitMarket()
            
    def onEnterOk(self, position):
        pass

    def onBars(self, bars):

        bar = bars[self.__instrument]
        
        if self.__mall[-1] is None:
            return
            
        self.testCon()            
            
        if self.__longPos is not None:

            if self.exitLongSignal():
                self.__longPos.exitMarket()
           
        elif self.__shortPos is not None:
            
            if self.exitShortSignal():
                self.__shortPos.exitMarket()

        elif self.__longPos is None and self.__shortPos is None:
            if self.enterLongSignal():
                shares = int(self.getBroker().getEquity() * 0.2 / bar.getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares)
                
            elif self.enterShortSignal():
                shares = int(self.getBroker().getEquity() * 0.2 / bar.getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares)


    def enterLongSignal(self) :
        if cross.cross_above(self.__mals, self.__mall) > 0:
            return True
    
    def enterShortSignal(self) :
        if cross.cross_below(self.__mals, self.__mall) > 0:
            return True
            
    def exitLongSignal(self) :
        if cross.cross_below(self.__mass, self.__masl) > 0 and not self.__longPos.exitActive():
            return True
            
    def exitShortSignal(self):
        if cross.cross_above(self.__mass, self.__masl) > 0 and not self.__shortPos.exitActive():
            return True


def testStrategy():
    from pyalgotrade import bar
    from pyalgotrade import plotter
    
    strat = fourSMA    
    instrument = '600288'
    market = 'SH'
    fromDate = '20150101'
    toDate ='20150601'
    frequency = bar.Frequency.MINUTE
    paras = [2, 20, 60, 10]
    plot = True
    
    #############################################path set ############################33 
    import os
    if frequency == bar.Frequency.MINUTE:
        path = os.path.join('..', 'histdata', 'minute')
    elif frequency == bar.Frequency.DAY:
        path = os.path.join('..', 'histdata', 'day')
    filepath = os.path.join(path, instrument + market + ".csv")
    
    
    #############################################don't change ############################33  
    from pyalgotrade.cn.csvfeed import Feed
    
    barfeed = Feed(frequency)
    barfeed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')
    barfeed.loadBars(instrument, market, fromDate, toDate, filepath)
    
    pyalgotrade_id = instrument + '.' + market
    strat = strat(barfeed, pyalgotrade_id, *paras)
    
    from pyalgotrade.stratanalyzer import returns
    from pyalgotrade.stratanalyzer import sharpe
    from pyalgotrade.stratanalyzer import drawdown
    from pyalgotrade.stratanalyzer import trades
    
    retAnalyzer = returns.Returns()
    strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)
    
    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        
    strat.run()
    
    if plot:
        plt.plot()
        


    #夏普率
    sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
    #最大回撤
    maxdd = drawDownAnalyzer.getMaxDrawDown()
    #收益率
    return_ = retAnalyzer.getCumulativeReturns()[-1]
    #收益曲线
    return_list = []
    for item in retAnalyzer.getCumulativeReturns():
        return_list.append(item)
        
        

if __name__ == "__main__": 
    testStrategy()
        
        
        
        
    