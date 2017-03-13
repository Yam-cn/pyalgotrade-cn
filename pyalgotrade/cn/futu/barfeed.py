# -*- coding: utf-8 -*-

"""
"""


import sys

import os

sys.path.append(os.path.dirname(__file__) + os.sep + '..'+ os.sep + '..'+ os.sep + '..') 
import Queue
import datetime
import time
from collections import deque
import pytz

#import open_quote as ft
import openft.open_quant_context as futu_open
import pyalgotrade.logger
from pyalgotrade.cn import bar
from pyalgotrade import barfeed
from pyalgotrade import dataseries
from pyalgotrade import resamplebase
from pyalgotrade.utils import dt
from pyalgotrade.bar import Frequency
from pyalgotrade.xignite.barfeed import utcnow

logger = pyalgotrade.logger.getLogger("futu")


def to_market_datetime(dateTime):
    timezone = pytz.timezone('Asia/Shanghai')
    return dt.localize(dateTime, timezone)

def get_futu_bar_list(df, frequency):
    
    bar_list = []
    
    for index, row in df.iterrows():
        open_ = row.open
        high = row.high
        low = row.low
        close = row.close
        volume = row.volume
        amount = row.turnover
        
        
        slice_start_time = datetime.datetime.strptime(row.time_key,'%Y-%m-%d %H:%M:%S')
        #time formate.
        slice_start_time = to_market_datetime(slice_start_time)
        bar_list.append(bar.BasicBar(slice_start_time, open_, high, low,
                                         close, volume, 0, frequency, amount))
    return bar_list

class CurKlineTest(futu_open.CurKlineHandlerBase):
    def __init__(self, queue, identifiers, last_kline_time):
        self.__queue = queue
        self.__identifiers = identifiers
        self.__last_kline_time = last_kline_time
    def on_recv_rsp(self, rsp_str):
        #ret_code, content = super().on_recv_rsp(rsp_str)
        ret_code, content = super(CurKlineTest, self).on_recv_rsp(rsp_str)
        print (ret_code)
        if ret_code != futu_open.RET_OK:
            print("CurKlineTest: error, msg: %s" % content)
            return futu_open.RET_ERROR, content
        print("CurKline : ", content)
        
        for index, row in content.iterrows():
            open_ = row.open
            high = row.high
            low = row.low
            close = row.close
            volume = row.volume
            amount = row.turnover
            slice_start_time = datetime.datetime.strptime(row.time_key,'%Y-%m-%d %H:%M:%S')
            slice_start_time = to_market_datetime(slice_start_time)
            identifier = row.code
            k_type = row.k_type
            if k_type != 'K_1M':
                continue
            if identifier not in self.__identifiers:
                continue
            
            if self.__last_kline_time[identifier] is None or self.__last_kline_time[identifier] < slice_start_time:
                self.__last_kline_time[identifier] = slice_start_time
            else:
                #print "slice_start_time %s last_kline_time %s", (slice_start_time, slice_start_time)
                continue
                        
            
            frequency = bar.Frequency.MINUTE
            one_bar = bar.BasicBar(slice_start_time, open_, high, low,
                                         close, volume, 0, frequency, amount)
            bar_dict = {}
            bar_dict[identifier] = one_bar
            bars = bar.Bars(bar_dict)
            self.__queue.put((FutuLiveFeed.ON_BARS, bars))

class FutuLiveFeed(barfeed.BaseBarFeed):
    QUEUE_TIMEOUT = 0.01
    ON_BARS = 1
    def __init__(self, identifiers, frequency, maxLen=dataseries.DEFAULT_MAX_LEN, get_his_kline_nums=50):
        barfeed.BaseBarFeed.__init__(self, frequency, maxLen)
        
        
        self.__quote_ctx = futu_open.OpenQuoteContext(host='119.29.141.202', async_port=11111)
        #self.__quote_ctx = futu_open.OpenQuoteContext(host='127.0.0.1', async_port=11111)
        if not isinstance(identifiers, list):
            raise Exception("identifiers must be a list")
        
        self.__identifiers = identifiers
        self.__frequency = frequency
        self.__queue = Queue.Queue()
        
        self.__last_kline_time = {} #the newest kline time
        for identifier in self.__identifiers:
            self.__last_kline_time[identifier] = None

        self.__fill_his_bars(get_his_kline_nums)# should run before polling thread start
        
        self.__quote_ctx.set_handler(CurKlineTest(self.__queue, self.__identifiers, self.__last_kline_time))
        self.__quote_ctx.start()
        self.__quote_ctx.subscribe('HK.00700', "K_1M", push=True)
        
        for instrument in identifiers:
            self.registerInstrument(instrument)
            print instrument

    ######################################################################
    # observer.Subject interface
    def start(self):
        pass

    def stop(self):
        pass

    def join(self):
        pass

    def eof(self):
        pass

    def peekDateTime(self):
        return None

    ######################################################################
    # barfeed.BaseBarFeed interface
    def getCurrentDateTime(self):
        return utcnow()

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        try:
            eventType, eventData = self.__queue.get(True, FutuLiveFeed.QUEUE_TIMEOUT)
            if eventType == FutuLiveFeed.ON_BARS:
                ret = eventData
            else:
                logger.error("Invalid event received: %s - %s" % (eventType, eventData))
        except Queue.Empty:
            pass
        return ret

    ######################################################################

    def __fill_bars(self, bars_dict):
        for index, value in enumerate(bars_dict[self.__identifiers[0]]):
            bar_dict = dict()
            #print index, value, "111"
            for identifier in self.__identifiers:
                if bars_dict[identifier][index] is not None:
                    #print "a", identifier
                    bar_dict[identifier] = bars_dict[identifier][index]
                    
                    kline_time = bar_dict[identifier].getDateTime()
                    
                    if self.__last_kline_time[identifier] is None or \
                       self.__last_kline_time[identifier] < kline_time:
                           self.__last_kline_time[identifier] = kline_time
                                         

            if len(bar_dict):
                bars = bar.Bars(bar_dict)
                self.__queue.put((FutuLiveFeed.ON_BARS, bars))

    def __fill_his_bars(self, num):
        bars_dict = {}
        
        for identifier in self.__identifiers:
            
            if self.__frequency==Frequency.MINUTE:
                ktype="K_1M"
            elif self.__frequency==Frequency.DAY:
                ktype="K_DAY"
                
            code=identifier
            self.__quote_ctx.subscribe(code, ktype)
            ret_code, ret_data = self.__quote_ctx.get_cur_kline(code, num, ktype)
            kline_table = ret_data
            print("file history bars %s KLINE %s" % (code, ktype))
            print(kline_table)
            print("\n\n")
            df=kline_table
            bars_dict[identifier] = get_futu_bar_list(df, self.__frequency)
            
        self.__fill_bars(bars_dict)
                
            
            

if __name__ == '__main__':
    market = 'HK'
    code1 = "HK.00700"
    code2 = "HK.00388"
    
    liveFeed = FutuLiveFeed([code1, code2], Frequency.MINUTE, dataseries.DEFAULT_MAX_LEN, 50)

    while True:
        bars = liveFeed.getNextBars()
        if bars is not None:
            print "have data"
            print code1, bars[code1].getHigh(), bars[code1].getDateTime(), bars[code1].getPrice()
            
        else :
            pass











