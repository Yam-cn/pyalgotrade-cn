# -*- coding: utf-8 -*-
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross,highlow
from pyalgotrade import technical
from pyalgotrade.technical import vwap
from pyalgotrade.stratanalyzer import sharpe
from pandas import DataFrame

from compiler.ast import flatten
import numpy as np

class SMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)
          
    def getSMA(self):
        return self.__sma
    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__prices, self.__sma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0:
            self.__position.exitMarket()

class VWAPMomentum(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, vwapWindowSize, threshold):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__feed = feed
        self.__threshold = threshold
        self.__vwap ={}
        for element in instrument:
            self.__vwap[element] = vwap.VWAP(feed[element], vwapWindowSize)
        self.__notional = 0
        self.__count = 0
        
        self.__info = DataFrame(columns={'date','id','action','instrument','quantity','price'})   #交易记录信息
        self.__info_matrix = []
   #手动增加日志信息，以获取数据，备网页显示,先单个交易的信息，多个交易暂时未写,从order中获取
    def addInfo(self,order):
        __date = order.getSubmitDateTime()  #时间
        __action = order.getAction()    #动作
        __id = order.getId()  #订单号
        __instrument = order.getInstrument()
        __quantity = order.getQuantity()  #数量
        __price = order.getAvgFillPrice()
        self.__info_matrix.append([__date,__id,__action,__instrument,__quantity,__price])
    
    #有多重实现方式和存储方式，考虑到组合数据，最终选用dataFrame且ID默认，因为或存在一日多单
    def getInfo(self):
        _matrix = np.array(self.__info_matrix).reshape((len(self.__info_matrix),6))
        return DataFrame({'date':_matrix[:,0],'id':_matrix[:,1],'action':_matrix[:,2],'instrument':_matrix[:,3],'quantity':_matrix[:,4],'price':_matrix[:,5]})  
    #对于组合取其并集
    def getDateTimeSeries(self,instrument=None):
        if instrument is None:
           __dateTime = DataFrame()
           for element in self.__instrument:
               __dateTime = __dateTime.append(self.__feed[element].getPriceDataSeries().getDateTimes())
           __dateTime = __dateTime.drop_duplicates([0])
           return __dateTime.values #此时返回的为二维数组
        return self.__feed[instrument].getPriceDataSeries().getDateTimes()
    def getVWAP(self):
        return self.__vwap

    def onBars(self, bars):
        for element in bars.getInstruments():#element in self.__instrument这种可能存在部分元素不在的情况
        
            self.__count+= 1
            vwap = self.__vwap[element][-1]
            if vwap is None:
                return
            shares = self.getBroker().getShares(element)
            price = bars[element].getClose()
            notional = shares * price
            
            if self.__count<30:
                print self.__count,element,shares,notional,self.getBroker().getCash(False),self.getBroker().getCash()
            self.__notional = notional   #记录上一次的值
            #print vwap,self.__notional
            if price > vwap * (1 + self.__threshold) and notional < 1000000:
                __order = self.marketOrder(element, 100)
                self.addInfo(__order)  #添加交易信息
                if(self.__count<30):
                    print "buy %s at ￥%.2f" % (element,price)
                #self.info("buy %s at ￥%.2f" % (element,price))
            elif price < vwap * (1 - self.__threshold) and notional > 0:
                __order = self.marketOrder(element, -100)  
                self.addInfo(__order)   #添加交易信息
                if(self.__count<30):
                    print "sell %s at ￥%.2f" % (element,price)
                #self.info("sell %s at ￥%.2f" % (element,price))

class turtle(strategy.BacktestingStrategy):
    def __init__(self,feed,instrument,N1,N2):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__feed = feed
        self.__position = None
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__high = highlow.High(self.__prices,N1,3)
        self.__low = highlow.Low(self.__prices,N2,3)
        self._count =0
        
        self.__info = DataFrame(columns={'date','id','action','instrument','quantity','price'})   #交易记录信息
        self.__info_matrix = []
   #手动增加日志信息，以获取数据，备网页显示,先单个交易的信息，多个交易暂时未写,从order中获取
    def addInfo(self,order):
        __date = order.getSubmitDateTime()  #时间
        __action = order.getAction()    #动作
        __id = order.getId()  #订单号
        __instrument = order.getInstrument()
        __quantity = order.getQuantity()  #数量
        __price = order.getAvgFillPrice()
        self.__info_matrix.append([__date,__id,__action,__instrument,__quantity,__price])
    
    #有多重实现方式和存储方式，考虑到组合数据，最终选用dataFrame且ID默认，因为或存在一日多单
    def getInfo(self):
        _matrix = np.array(self.__info_matrix).reshape((len(self.__info_matrix),6))
        return DataFrame({'date':_matrix[:,0],'id':_matrix[:,1],'action':_matrix[:,2],'instrument':_matrix[:,3],'quantity':_matrix[:,4],'price':_matrix[:,5]}) 
    #返回某一instrument的时间序列
    def getDateTimeSeries(self,instrument=None):   #海龟交易法和vwamp方法不一样，一个instrument为数组，一个为值
        if instrument is None:
            return self.__feed[self.__instrument].getPriceDataSeries().getDateTimes()
        return self.__feed[instrument].getPriceDataSeries().getDateTimes()
        
    def getHigh(self):
        return self.__high
        
    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at ￥%.2f" % (execInfo.getPrice()))
        self.addInfo(position.getEntryOrder())   #在此处添加信息
        
    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at ￥%.2f" % (execInfo.getPrice()))
        self.addInfo(position.getExitOrder())  #在此处添加信息
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        #若使用self__high[-1]这种值的话，不能是none,self.__high[0:0]为取前一日的  #也可以self.__high.__len__()！=3
            if self.__high.__len__() is not 3:   
                return
            bar = bars[self.__instrument]
            # If a position was not opened, check if we should enter a long position.
            #如果不设定high的长度为3的话，可能取不到-3的值
            if self.__position is None or not self.__position.isOpen() :  
                #判定今天价比昨日的最高价高，昨天价比前天的最高价低
                if self.__prices[-1]>self.__high[-2] and self.__prices[-2]<self.__high[-3]:
                    shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                    # Enter a buy market order. The order is good till canceled.
                    self.__position = self.enterLong(self.__instrument, shares, True)  #多种实现方式，为记录信息简要写于一处
                  
            # Check if we have to exit the position.
            elif not self.__position.exitActive() and self.__prices[-1]<self.__low[-2] and self.__prices[-2]>self.__low[-3]:
                self.__position.exitMarket()
              
