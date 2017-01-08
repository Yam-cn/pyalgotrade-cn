# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 13:06:56 2015

@author: Zhixiong Ge (james.ge@gmail.com)
"""
from pyalgotrade.cn.CTP.barfeed import CTPLiveFeed
from pyalgotrade.cn.CTP.livebroker import LiveBroker
from pyalgotrade import strategy


class TestStrategy(strategy.BaseStrategy):
    def __init__(self, feed, brk):
        strategy.BaseStrategy.__init__(self, feed, brk)
        self.__instruments = feed.getRegisteredInstruments()
        self.__position = {}
        
        self.bar_count = 0
        
        
    def onEnterOk(self, position):
        print '___________________________________'
        print 'onEnterOK called'
        
        
    def onExitOk(self, position):
        print '___________________________________'
        print 'onExitOk called'
        self.__position = {}
        
        
    def onBars(self, bars):
        self.bar_count += 1
        # If a position was not opened, check if we should enter a long position.
        
        print 'onBars called'
        
        for ticker in self.__instruments:
            b = bars.getBar(ticker)
            if b:
                print 'time', b.getDateTime(), 'open:',b.getOpen(),  'high:', b.getHigh(), ' low: ', b.getLow(), \
                    'close: ', b.getClose(), 'volume:', b.getVolume(), 'amount:', b.getAmount()
                    
        print 'cash:{0}'.format(self.getBroker().getCash())
        
        
        if len(self.__position) > 0:
            if self.bar_count == 2:
                print 'cancelling order'
                self.__position.values()[0].cancelEntry()
                self.__position = {}
            else:
                print 'sending sell order'
                self.__position.values()[0].exitLimit(int(b.getClose() * 0.99), goodTillCanceled=None)
            #self.__position.exitMarket()                
            
        
        if len(self.__position) == 0:
            print 'sending buy order'
            if self.bar_count == 1:
                pos = self.enterLongLimit(self.__instruments[0], int(b.getClose() * 0.99), 1)
                self.__position[pos.getEntryOrder().getId()] = pos
            else:
                pos = self.enterLongLimit(self.__instruments[0], int(b.getClose() * 1.01), 1)
                self.__position[pos.getEntryOrder().getId()] = pos
            #print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
            
    
if __name__ == "__main__":
    ticker = 'ag1706'
    
    feed = CTPLiveFeed([ticker], 10)
    brk = LiveBroker('052677')
    
    strat = TestStrategy(feed, brk)    
    strat.run()
    
    


    























