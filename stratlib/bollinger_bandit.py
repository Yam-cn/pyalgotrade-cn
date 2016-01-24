# -*- coding: utf-8 -*-
"""
Created on Tue Dec 01 10:12:01 2015

@author: Eunice 
"""


# 以下模块仅测试用
import sys
sys.path.append("..\\")
from pyalgotrade import plotter
from pyalgotrade import bar
from pyalgotrade import dataseries
# 以上模块仅测试用
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade import strategy
from pyalgotrade.dataseries import SequenceDataSeries
from pyalgotrade.technical import cross
import numpy as np
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade.technical import bollinger





class Bollinger_Bandit(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bollingerlength, numStdDev, closelength, ccMAlength, malength, space):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.002))
        self.__instrument = instrument
        self.__bollingerlength = int(bollingerlength)
        numStdDev = float(numStdDev) / 10
        self.__closelength = int(closelength)
        self.__ccMAlength = int(ccMAlength)
        self.__malength = int(malength)
        self.__longPos = None
        self.__shortPos = None
        self.__close = feed[instrument].getCloseDataSeries()
        self.__high = feed[instrument].getHighDataSeries()
        self.__low = feed[instrument].getLowDataSeries()
        self.__datetime = feed[instrument].getDateTimes()
        self.__bollinger = bollinger.BollingerBands(self.__close, self.__bollingerlength, int(numStdDev))
        self.__UpperBand = self.__bollinger.getUpperBand()
        self.__LowerBand = self.__bollinger.getLowerBand()
        self.__MA = SequenceDataSeries()
        self.__space = int(space)
        self.__enter = 0
        self.__enterLong1 = 0
        self.__enterLong2 = 0
        self.__enterShort1 = 0
        self.__enterShort2 = 0
        self.__exitLong1 = 0
        self.__exitLong2 = 0
        self.__exitShort1 = 0
        self.__exitShort1 = 0
        
        #for test
        #########################################################################
        self.__p = SequenceDataSeries()
        self.__filterCon = SequenceDataSeries()
        self.__ccMACon1 = SequenceDataSeries()
        self.__ccMACon2 = SequenceDataSeries()
        self.__enterCon = SequenceDataSeries()
        self.__enterLongCon1 = SequenceDataSeries()
        self.__enterLongCon2 = SequenceDataSeries()
        self.__enterShortCon1 = SequenceDataSeries()
        self.__enterShortCon2 = SequenceDataSeries()
        self.__exitLongCon1 = SequenceDataSeries()
        self.__exitLongCon2 = SequenceDataSeries()
        self.__exitShortCon1 = SequenceDataSeries()
        self.__exitShortCon2 = SequenceDataSeries()
        ##########################################################################
              
    def getHigh(self):
        return self.__high
        
    def getLow(self):
        return self.__low
        
    def getClose(self):
        return self.__close
    
    def getBollinger(self):
        return self.__UpperBand, self.__LowerBand
        
    def getMA(self):
        return self.__MA
        
    def getDateTime(self):
        return self.__datetime
        
    def getPosition(self):
        return self.__p
        
    def getTest(self):
        return self.__filterCon, self.__ccMACon1, self.__ccMACon2, \
        self.__enterCon, self.__enterLongCon1, self.__enterLongCon2, self.__enterShortCon1, \
        self.__enterShortCon2, self.__exitLongCon1, self.__exitLongCon2, \
        self.__exitShortCon1, self.__exitShortCon2
              
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

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        
        bar = bars[self.__instrument]
        
        # filter datetime    
        ###################################################################################        
        filterCon = len(self.__close) < max(self.__bollingerlength, self.__malength, self.__closelength)
        self.__filterCon.append(filterCon)
        
        if filterCon:
            return
     
        # record position      
        ####################################################################################
        if self.__longPos is not None and self.__shortPos is None:
            self.__p.append(1) 
        elif self.__longPos is None and self.__shortPos is not None:
            self.__p.append(-1)
        else:
            self.__p.append(0)   
  
        # calculate ccMA     
        ####################################################################################           
        ccMACon1 = self.__longPos is not None or self.__shortPos is not None
        ccMACon2 = self.__malength > self.__ccMAlength
        
        if ccMACon1 and ccMACon2: 
            self.__malength = self.__malength - 1
        elif not ccMACon1:
            self.__malength = 50

        self.__ccMA = np.mean(self.__close[-self.__malength:])
#        print self.__malength, self.__ccMA
        self.__MA.append(self.__ccMA)
        self.__ccMACon1.append(ccMACon1)
        self.__ccMACon2.append(ccMACon2)
        
        #open and close condition   
        ######################################################################################   
        self.__enterLong1 = (cross.cross_above(self.__high, self.__UpperBand) > 0)
        self.__enterLong2 = (bar.getClose() >= max(self.__close[-self.__closelength:]))
        self.__enter = ((self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose() > float(self.__space) / 1000)
#        print (self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose()
        self.__enterShort1 = cross.cross_below(self.__low, self.__LowerBand) > 0 
        self.__enterShort2 = bar.getClose() <= min(self.__close[-self.__closelength:])
        self.__exitLong1 = (bar.getClose() < self.__ccMA)
        self.__exitLong2 = (self.__ccMA < self.__UpperBand[-1])
        self.__exitShort1 = (bar.getClose() > self.__ccMA)
        self.__exitShort2 = (self.__ccMA > self.__LowerBand[-1])
        
        self.__enterCon.append(self.__enter)
        self.__enterLongCon1.append(self.__enterLong1)
        self.__enterLongCon2.append(self.__enterLong2)
        self.__enterShortCon1.append(self.__enterShort1)
        self.__enterShortCon2.append(self.__enterShort2)
        self.__exitLongCon1.append(self.__exitLong1)
        self.__exitLongCon2.append(self.__exitLong2)
        self.__exitShortCon1.append(self.__exitShort1)
        self.__exitShortCon2.append(self.__exitShort2)
  
        #open and close  
        #######################################################################################        
        if self.__longPos is not None:         
             if self.exitLongSignal():
                 self.__longPos.exitMarket()
#             if self.__shortPos is not None:
#                 print 11
#                 self.info("intend long close")
#                 print (self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose()
                 
        elif self.__shortPos is not None:
             if self.exitShortSignal():
                  self.__shortPos.exitMarket()
#                  self.info("intend short close")
#                  print (self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose()
                  
        else:
             if self.enterLongSignal():
                 shares = int(self.getBroker().getCash() * 0.2 / bars[self.__instrument].getPrice())
                 self.__longPos = self.enterLong(self.__instrument, shares)
#                 self.info("intend long open")
#                 print (self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose()
              
             elif self.enterShortSignal():
                 shares = int(self.getBroker().getCash() * 0.2 / bars[self.__instrument].getPrice())
                 self.__shortPos = self.enterShort(self.__instrument, shares)
#                 self.info("intend short open")
#                 print (self.__UpperBand[-1] - self.__LowerBand[-1]) / bar.getClose()
                 
    def enterLongSignal(self):
        if self.__enterLong1 and self.__enterLong2 and self.__enter:
            return True
    
    def enterShortSignal(self):
        if self.__enterShort1 and self.__enterShort2 and self.__enter:
            return True
            
    def exitLongSignal(self):
        if self.__exitLong1 and self.__exitLong2 and not self.__longPos.exitActive():
            return True
            
    def exitShortSignal(self):
        if self.__exitShort1 and self.__exitShort2 and not self.__shortPos.exitActive():
            return True 



if __name__ == "__main__":
    #############################################para set ############################33    
    strat = Bollinger_Bandit    
    instrument = '000001'
    market = 'SZ'
    fromDate = '20120101'
    toDate ='20160101'
    frequency = bar.Frequency.DAY
    paras = [40, 15, 35, 15, 60, 2]
    plot = True
    
    #############################################path set ############################33 
    if frequency == bar.Frequency.MINUTE:
        path = "..\\histdata\\min\\"
    elif frequency == bar.Frequency.DAY:
        path = "..\\histdata\\day\\"
    filepath = path + instrument + market + ".csv"
    
    
    #############################################don't change ############################33  
    from pyalgotrade.bar import Frequency
    from pyalgotrade.barfeed.csvfeed import GenericBarFeed

    
    barfeed = GenericBarFeed(Frequency.DAY)
    barfeed.addBarsFromCSV(instrument, filepath)
    strat = strat(barfeed, instrument, *paras)
    
    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        
    strat.run()
    
    if plot:
        plt.plot()

    





































