# -*- coding: utf-8 -*-
"""
Created on Sat Sep 03 16:52:59 2016

@author: James
"""
import pandas as pd
from datetime import datetime

from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade import dataseries
from pyalgotrade.cn.bar import BasicBar
from pyalgotrade.cn.bar import Frequency
from pyalgotrade.cn.pandasfeed import dataframeToBar
from pyalgotrade.cn.pandasfeed import dataframeToTick

    
class Feed(membf.BarFeed):
    def __init__(self, frequency, maxLen=dataseries.DEFAULT_MAX_LEN):
        membf.BarFeed.__init__(self, frequency, maxLen)
        self.__frequency = frequency
        
    def barsHaveAdjClose(self):
        return False
        
    def setDateTimeFormat(self, iformat):
        self._datetime_format = iformat

    def loadBars(self, instrument_id, exchange_id, fromdate, todate, path):
        try:
            fromdate = datetime.strptime(fromdate, '%Y%m%d')
            todate = datetime.strptime(todate, '%Y%m%d')
        except Exception:
            raise Exception('invalid date format, e.g. 20160206')
            
        idataframe = pd.read_csv(path)
        idataframe.ix[:, 'datetime'] = idataframe.ix[:, 'datetime'].apply(lambda x: datetime.strptime(x, self._datetime_format))
        idataframe = idataframe[(idataframe.datetime >= fromdate) & (idataframe.datetime <= todate)]
        bars = dataframeToBar(idataframe, self.__frequency)
        pyalgotrade_id = instrument_id + '.' + exchange_id
        self.addBarsFromSequence(pyalgotrade_id, bars)
        return
        
        
    def loadTicks(self, instrument_id, exchange_id, fromdate, todate, path):
        try:
            fromdate = datetime.strptime(fromdate, '%Y%m%d')
            todate = datetime.strptime(todate, '%Y%m%d')
        except Exception:
            raise Exception('invalid date format, e.g. 20160206')
            
        idataframe = pd.read_csv(path)
        idataframe = idataframe.sort_values(by = 'datetime')
        idataframe.ix[:, 'datetime'] = idataframe.ix[:, 'datetime'].apply(lambda x: datetime.strptime(x, self._datetime_format))
        idataframe = idataframe[(idataframe.datetime >= fromdate) & (idataframe.datetime <= todate)]
        bars = dataframeToTick(idataframe, self.__frequency)
        pyalgotrade_id = instrument_id + '.' + exchange_id
        self.addBarsFromSequence(pyalgotrade_id, bars)
        return
        
            
    def closeDB(self):
        self.__db.closeDB()
        
        
if __name__ == '__main__':
    pass
    
    
    
    
    
    
    
    
    