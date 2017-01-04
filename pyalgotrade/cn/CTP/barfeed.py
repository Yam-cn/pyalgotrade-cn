# Copyright 2011-2016 ZackZK
# coding:utf-8
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
.. moduleauthor:: ZackZK <silajoin@sina.com>
"""
import Queue

import pytz

from api.CTPMdApi import CTPMdApi

from pyalgotrade.cn import bar
from pyalgotrade import barfeed
from pyalgotrade import resamplebase
from pyalgotrade.utils import dt
from pyalgotrade.xignite.barfeed import PollingThread, utcnow

from threading import Lock

from pandas import DataFrame

import pyalgotrade.logger
logger = pyalgotrade.logger.getLogger("CTP")

def to_market_datetime(dateTime):
    timezone = pytz.timezone('Asia/Shanghai')
    return dt.localize(dateTime, timezone)

class GetBarThread(PollingThread):
    # Events
    ON_BARS = 1

    def __init__(self, queue, identifiers, frequency):
        super(GetBarThread, self).__init__()

        self.__queue = queue
        self.__identifiers = identifiers
        self.__frequency = frequency
        self.__nextBarStart = None
        self.__nextBarClose = None

        self._ticksDf = {}
        self.__lock = Lock()

        for identifier in self.__identifiers:
            self._ticksDf[identifier] = DataFrame(columns=['time', 'price', 'volume', 'amount'])

        self._ctpMdApi = CTPMdApi(self.__identifiers, self._ticksDf, self.__lock, logger)
        #self._ctpMdApi.login("tcp://222.66.97.241:41213", '9017811', '123456', '7070')
        self._ctpMdApi.login("tcp://180.168.212.228:41213","simnow申请", "simnow申请", "9999")
        #self._ctpMdApi.login("tcp://211.144.195.163:34505", "", "", "")

        self.__updateNextBarClose()

    def __updateNextBarClose(self):
        self.__nextBarStart = resamplebase.build_range(utcnow(), self.__frequency).getBeginning()
        self.__nextBarClose = resamplebase.build_range(utcnow(), self.__frequency).getEnding()

    def getNextCallDateTime(self):
        return self.__nextBarClose

    def doCall(self):
        startDateTime = to_market_datetime(self.__nextBarStart)
        endDateTime = to_market_datetime(self.__nextBarClose)
        self.__updateNextBarClose()
        barDict = dict()

        for identifier in self.__identifiers:
            try:
                period_bar = self._build_bar(identifier, startDateTime, endDateTime)
                if period_bar:
                    barDict[identifier] = period_bar

            except Exception, e:
                logger.error(e)

        if len(barDict):
            bars = bar.Bars(barDict)
            self.__queue.put((GetBarThread.ON_BARS, bars))

    def _build_bar(self, identifier, start, end):

        df = self._ticksDf[identifier]

        ticks_slice = df.ix[(df.time < end.strftime("%H:%M:%S")) &
                            (df.time >= start.strftime("%H:%M:%S"))]

        if not ticks_slice.empty:
            open_ = ticks_slice.price.get_values()[0]
            high = max(ticks_slice.price)
            low = min(ticks_slice.price)
            close = ticks_slice.price.get_values()[-1]
            volume = sum(ticks_slice.volume)
            amount = sum(ticks_slice.amount)

            return bar.BasicBar(to_market_datetime(start), open_, high, low, close, volume,
                                amount, self.__frequency, {})
        else:
            return None


class CTPLiveFeed(barfeed.BaseBarFeed):
    QUEUE_TIMEOUT = 0.01

    def __init__(self, identifiers, frequency):
        super(CTPLiveFeed, self).__init__(frequency)

        if not isinstance(identifiers, list):
            raise Exception("identifiers must be a list")

        self.__identifiers = identifiers
        self.__queue = Queue.Queue()

        self._thread = GetBarThread(self.__queue, identifiers, frequency)

        for instrument in identifiers:
            self.registerInstrument(instrument)

    ######################################################################
    # observer.Subject interface

    def start(self):
        if self._thread.is_alive():
            raise Exception("Already strated")

        # Start the thread that runs the client.
        self._thread.start()

    def stop(self):
        self._thread.stop()

    def join(self):
        if self._thread.is_alive():
            self._thread.join()

    def eof(self):
        return self._thread.stopped()

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
            eventType, eventData = self.__queue.get(True, CTPLiveFeed.QUEUE_TIMEOUT)
            if eventType == GetBarThread.ON_BARS:
                ret = eventData
            else:
                logger.error("Invalid event received: %s - %s" % (eventType, eventData))
        except Queue.Empty:
            pass
        return ret
        
        
def test_feed():
    feed = CTPLiveFeed(['au1702', 'ag1702'], 30)
    feed.start()
    while True:
        bars = feed.getNextBars()
        if bars:
            b = bars.getBar('au1702')
            if b:
                print '__________________au__________________'
                print 'time', b.getDateTime(), 'open:',b.getOpen(),  'high:', b.getHigh(), ' low: ', b.getLow(), \
                    'close: ', b.getClose(), 'volume:', b.getVolume(), 'amount:', b.getAmount()
                    
                    
            b = bars.getBar('ag1702')
            if b:
                print '__________________ag__________________'
                print 'time', b.getDateTime(), 'open:',b.getOpen(),  'high:', b.getHigh(), ' low: ', b.getLow(), \
                    'close: ', b.getClose(), 'volume:', b.getVolume(), 'amount:', b.getAmount()


if __name__ == '__main__':
    test_feed()
    
