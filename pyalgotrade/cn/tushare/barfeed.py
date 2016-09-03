# Copyright 2011-2015 ZackZK
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
import datetime
import threading
import time
from collections import deque
import pytz

import tushare as ts
# from tushare.util.dateu import is_holiday  # use our own is_holiday currently as tushare does not include 2016 holiday

import pyalgotrade.logger
from pyalgotrade.cn import bar
from pyalgotrade import barfeed
from pyalgotrade import dataseries
from pyalgotrade import resamplebase
from pyalgotrade.utils import dt
from pyalgotrade.bar import Frequency
from pyalgotrade.xignite.barfeed import utcnow

logger = pyalgotrade.logger.getLogger("tushare")


def to_market_datetime(dateTime):
    timezone = pytz.timezone('Asia/Shanghai')
    return dt.localize(dateTime, timezone)


holiday = ['2015-01-01', '2015-01-02', '2015-02-18', '2015-02-19', '2015-02-20', '2015-02-23', '2015-02-24',
           '2015-04-06', '2015-05-01', '2015-06-22', '2015-09-03', '2015-09-04', '2015-10-01', '2015-10-02',
           '2015-10-05', '2015-10-06', '2015-10-07',
           '2016-01-01', '2016-02-08', '2016-02-09', '2016-02-10', '2016-02-11', '2016-02-12', '2016-04-04',
           '2016-05-02', '2016-06-09', '2016-06-10', '2016-09-15', '2016-09-16', '2016-10-03', '2016-10-04',
           '2016-10-05', '2016-10-06', '2016-10-07']


def is_holiday(date):
    if isinstance(date, str):
        today = datetime.datetime.strptime(date, '%Y-%m-%d')

    if today.isoweekday() in [6, 7] or date in holiday:
        return True
    else:
        return False


class TickDataSeries(object):
    def __init__(self):
        self.__priceDS = deque()
        self.__volumeDS = deque()
        self.__amountDS = deque()
        self.__dateTimes = deque()  # just for debug

    def reset(self):
        self.__priceDS.clear()
        self.__volumeDS.clear()
        self.__amountDS.clear()
        self.__dateTimes.clear()

    def getPriceDS(self):
        return self.__priceDS

    def getAmountDS(self):
        return self.__amountDS

    def getVolumeDS(self):
        return self.__volumeDS

    def getDateTimes(self):
        return self.__dateTimes

    def append(self, price, volume, amount, dateTime):
        assert(bar is not None)
        self.__priceDS.append(price)
        self.__volumeDS.append(volume)
        self.__amountDS.append(amount)
        self.__dateTimes.append(dateTime)

    def empty(self):
        return len(self.__priceDS) == 0


def get_trading_days(start_day, days):
    try:
        df = ts.get_hist_data('sh')
    except Exception, e:
        logger.error("Tushare get hist data exception", exc_info=e)
        return []

    trading_days = list()
    holiday = 0

    for i in range(days):
        while True:
            day = start_day - datetime.timedelta(days=i+1+holiday)
            if day.date().isoformat() in df.index:
                trading_days.append(day)
                break
            else:
                holiday += 1

    trading_days.reverse()  # oldest date is put to head

    return trading_days


def build_bar(dateTime, ds):
    prices = ds.getPriceDS()
    volumes = ds.getVolumeDS()
    amounts = ds.getAmountDS()

    open_ = float(prices[0])
    high = float(max(prices))
    low = float(min(prices))
    close = float(prices[-1])
    volume = sum(int(v) for v in volumes)
    amount = sum(float(a) for a in amounts)

    return bar.BasicBar(dateTime, open_, high, low, close, volume, None, Frequency.DAY, amount)


class TuSharePollingThread(threading.Thread):
    # Not using xignite polling thread is because two underscores functions can't be override, e.g. __wait()

    TUSHARE_INQUERY_PERIOD = 3 # tushare read period, default is 3s

    def __init__(self, identifiers):
        super(TuSharePollingThread, self).__init__()
        self._identifiers = identifiers
        self._tickDSDict = {}
        self._last_quotation_time = {}

        for identifier in self._identifiers:
            self._tickDSDict[identifier] = TickDataSeries()
            self._last_quotation_time[identifier] = None

        self.__stopped = False

    def __wait(self):
        # first reset ticks info in one cycle, maybe we need save it if NO quotation in this period
        for identifier in self._identifiers:
            self._tickDSDict[identifier].reset()

        nextCall = self.getNextCallDateTime()

        while not self.__stopped and utcnow() < nextCall:
            start_time = datetime.datetime.now()

            self.get_tushare_tick_data()

            end_time = datetime.datetime.now()
            time_diff = (end_time - start_time).seconds

            if time_diff < TuSharePollingThread.TUSHARE_INQUERY_PERIOD:
                time.sleep(TuSharePollingThread.TUSHARE_INQUERY_PERIOD - time_diff)

    def valid_tick_data(self, identifier, tick_info):
        if self._last_quotation_time[identifier] is None or \
                        self._last_quotation_time[identifier] < tick_info.time:
            self._last_quotation_time[identifier] = tick_info.time
        else:
            return False

        return float(tick_info.pre_close) * 0.9 <= float(tick_info.price) <= float(tick_info.pre_close) * 1.1

    def get_tushare_tick_data(self):
        try:
            df = ts.get_realtime_quotes(self._identifiers)

            for index, identifier in enumerate(self._identifiers):
                tick_info = df.ix[index]

                if self.valid_tick_data(identifier, tick_info):
                    # tushare use unicode type, another way is convert it to int/float here. refer to build_bar
                    self._tickDSDict[identifier].append(tick_info.price, tick_info.volume, tick_info.amount,
                                                        tick_info.time)
        except Exception, e:
            logger.error("Tushare polling exception", exc_info=e)

    def stop(self):
        self.__stopped = True

    def stopped(self):
        return self.__stopped

    def run(self):
        logger.debug("Thread started.")
        while not self.__stopped:
            self.__wait()
            if not self.__stopped:
                try:
                    self.doCall()
                except Exception, e:
                    logger.critical("Unhandled exception", exc_info=e)
        logger.debug("Thread finished.")

    # Must return a non-naive datetime.
    def getNextCallDateTime(self):
        raise NotImplementedError()

    def doCall(self):
        raise NotImplementedError()


class TushareBarFeedThread(TuSharePollingThread):
    # Events
    ON_BARS = 1

    def __init__(self, queue, identifiers, frequency):
        super(TushareBarFeedThread, self).__init__(identifiers)
        self.__queue = queue
        self.__frequency = frequency
        self.__updateNextBarClose()

    def __updateNextBarClose(self):
        self.__nextBarClose = resamplebase.build_range(utcnow(), self.__frequency).getEnding()

    def getNextCallDateTime(self):
        return self.__nextBarClose

    def doCall(self):
        endDateTime = self.__nextBarClose
        self.__updateNextBarClose()
        bar_dict = {}

        for identifier in self._identifiers:
            try:
                if not self._tickDSDict[identifier].empty():
                    bar_dict[identifier] = build_bar(to_market_datetime(endDateTime), self._tickDSDict[identifier])
            except Exception, e:
                logger.error(e)

        if len(bar_dict):
            bars = bar.Bars(bar_dict)
            self.__queue.put((TushareBarFeedThread.ON_BARS, bars))


def get_bar_list(df, frequency, date=None):
    bar_list = []

    end_time = df.ix[0].time
    if date is None:
        date = datetime.datetime.now()
    slice_start_time = to_market_datetime(datetime.datetime(date.year, date.month , date.day, 9, 30, 0))

    while slice_start_time.strftime("%H:%M:%S") < end_time:
        slice_end_time = slice_start_time + datetime.timedelta(seconds=frequency)

        ticks_slice = df.ix[(df.time < slice_end_time.strftime("%H:%M:%S")) &
                            (df.time >= slice_start_time.strftime("%H:%M:%S"))]

        if not ticks_slice.empty:
            open_ = ticks_slice.price.get_values()[-1]
            high = max(ticks_slice.price)
            low = min(ticks_slice.price)
            close = ticks_slice.price.get_values()[0]
            volume = sum(ticks_slice.volume)
            amount = sum(ticks_slice.amount)

            bar_list.append(bar.BasicBar(slice_start_time, open_, high, low,
                                         close, volume, 0, frequency, amount))
        else:
            bar_list.append(None)
        slice_start_time = slice_end_time

    return bar_list


class TuShareLiveFeed(barfeed.BaseBarFeed):
    QUEUE_TIMEOUT = 0.01

    def __init__(self, identifiers, frequency, maxLen=dataseries.DEFAULT_MAX_LEN, replayDays=-1):
        barfeed.BaseBarFeed.__init__(self, frequency, maxLen)
        if not isinstance(identifiers, list):
            raise Exception("identifiers must be a list")

        self.__identifiers = identifiers
        self.__frequency = frequency
        self.__queue = Queue.Queue()

        self.__fill_today_history_bars(replayDays) # should run before polling thread start

        self.__thread = TushareBarFeedThread(self.__queue, identifiers, frequency)
        for instrument in identifiers:
            self.registerInstrument(instrument)

    ######################################################################
    # observer.Subject interface
    def start(self):
        if self.__thread.is_alive():
            raise Exception("Already strated")

        # Start the thread that runs the client.
        self.__thread.start()

    def stop(self):
        self.__thread.stop()

    def join(self):
        if self.__thread.is_alive():
            self.__thread.join()

    def eof(self):
        return self.__thread.stopped()

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
            eventType, eventData = self.__queue.get(True, TuShareLiveFeed.QUEUE_TIMEOUT)
            if eventType == TushareBarFeedThread.ON_BARS:
                ret = eventData
            else:
                logger.error("Invalid event received: %s - %s" % (eventType, eventData))
        except Queue.Empty:
            pass
        return ret

    ######################################################################
    # TuShareLiveFeed own interface
    def _fill_today_bars(self):
        today = datetime.date.today().isoformat()

        if is_holiday(today):  # do nothing if holiday
            return
        elif datetime.date.today().weekday() in [5, 0]:
            return
        
#        #James:
#        if datetime.datetime.now().hour * 60 + 30 < 9*60 + 30:
#            return

        today_bars = {}
        for identifier in self.__identifiers:
            try:
                df = ts.get_today_ticks(identifier)
                today_bars[identifier] = get_bar_list(df, self.__frequency, None)
            except Exception, e:
                logger.error(e)

        self.__fill_bars(today_bars)

    def __fill_bars(self, bars_dict):
        for index, value in enumerate(bars_dict[self.__identifiers[0]]):
            bar_dict = dict()
            for identifier in self.__identifiers:
                if bars_dict[identifier][index] is not None:
                    bar_dict[identifier] = bars_dict[identifier][index]

            if len(bar_dict):
                bars = bar.Bars(bar_dict)
                self.__queue.put((TushareBarFeedThread.ON_BARS, bars))

    def _fill_history_bars(self, replay_days):
        now = datetime.datetime.now()
        for day in get_trading_days(now, replay_days):
            bars_dict = {}

            for identifier in self.__identifiers:
                df = ts.get_tick_data(identifier, date=day.date().isoformat())
                bars_dict[identifier] = get_bar_list(df, self.__frequency, day)

            self.__fill_bars(bars_dict)

    def __fill_today_history_bars(self, replayDays):
        if replayDays < 0:  # only allow -1 and >=0 integer value
            replayDays = -1
        if replayDays == -1:
            pass
        elif replayDays == 0:  # replay today's quotation
            self._fill_today_bars()
        else:
            self._fill_history_bars(replayDays)
            self._fill_today_bars()


if __name__ == '__main__':
    liveFeed = TuShareLiveFeed(['000581'], Frequency.MINUTE, dataseries.DEFAULT_MAX_LEN, 2)
    liveFeed.start()

    while not liveFeed.eof():
        bars = liveFeed.getNextBars()
        if bars is not None:
            print bars['000581'].getHigh(), bars['000581'].getDateTime()
            # test/












