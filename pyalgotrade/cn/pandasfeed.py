# -*- coding: utf-8 -*-
"""
Created on Sat Sep 03 16:52:59 2016

@author: James
"""
import pandas as pd

from pyalgotrade.barfeed import membf
from pyalgotrade import dataseries
from pyalgotrade.cn import bar
    

def dataframeToBar(bar_dataframe, frequency):
    bars = []
    for _, row in bar_dataframe.iterrows():
        tmp_extra = {}
        for key in row.keys():
            if key not in ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']:
                tmp_extra[key] = row[key]
        bars.append(bar.BasicBar(row['datetime'], row['open'], row['high'], row['low'], row['close'], row['volume']\
                 , row['amount'], frequency, False, tmp_extra))
    return bars
    
    
def dataframeToTick(tick_dataframe, frequency):
    ticks = []
    for _, row in tick_dataframe.iterrows():
        tmp_extra = {}
        tmp_ap = {}
        tmp_bp = {}
        tmp_av = {}
        tmp_bv = {}
        for key in row.keys():
            #extract order book component 
            if key[:2] == 'ap':
                tmp_ap[int(key[2:])] = row[key]
                continue
                
            elif key[:2] == 'bp':
                tmp_bp[int(key[2:])] = row[key]
                continue

            elif key[:2] == 'av':
                tmp_av[int(key[2:])] = row[key]
                continue
                
            elif key[:2] == 'bv':
                tmp_bv[int(key[2:])] = row[key]
                continue                
                
            #extract extra component
            if key not in ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'preclose'\
                         , 'new_price', 'bought_amount', 'sold_amount', 'bought_volume', 'sold_volume'\
                         , 'frequency']:
                tmp_extra[key] = row[key]

                
        ticks.append(bar.BasicTick(row['datetime'], row['open'], row['high'], row['low'], row['close'], row['volume']\
                 , row['amount'], tmp_bp, tmp_bv, tmp_ap, tmp_av, row['preclose'], row['bought_volume']\
                 , row['sold_volume'], row['bought_amount'], row['sold_amount'], frequency, False, tmp_extra))
    return ticks

    
class Feed(membf.BarFeed):
    def __init__(self, frequency, maxLen=dataseries.DEFAULT_MAX_LEN):
        membf.BarFeed.__init__(self, frequency, maxLen)
        self.__frequency = frequency
        
    def barsHaveAdjClose(self):
        return False

    def loadBars(self, instrument_id, exchange_id, idataframe):         
        bars = dataframeToBar(idataframe, self.__frequency)
        pyalgotrade_id = instrument_id + '.' + exchange_id
        self.addBarsFromSequence(pyalgotrade_id, bars)
        return
            
    def closeDB(self):
        self.__db.closeDB()
        
        
if __name__ == '__main__':
    pass
    
    
    
    
    
    
    
    
    