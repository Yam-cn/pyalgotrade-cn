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
from unittest import TestCase
import mock

from pyalgotrade.CTP.api.CTPMdApi import CTPMdApi
from pandas import DataFrame
from threading import Lock


class TestCTPMdApi(TestCase):
    def setUp(self):
        self._instrument = 'au1606'
        ticks_df = dict()
        lock = Lock()
        self._logger = mock.MagicMock()

        self._df = DataFrame(columns=['time', 'price', 'volume', 'amount'])
        ticks_df[self._instrument] = self._df

        self._api = CTPMdApi([self._instrument], ticks_df, lock, self._logger)

    def test_onRtnDepthMarketData(self):
        data = dict()
        data['InstrumentID'] = self._instrument
        data['UpdateTime'] = '09:31:00'
        data['LastPrice'] = 10.0
        data['Volume'] = 200
        data['Turnover'] = 412.3
        data['PreClosePrice'] = 10.0
        self._api.onRtnDepthMarketData(data)

        self.assertEqual(1, len(self._df))
        self.assertEqual(10.0, self._df.ix[0].price)
        self.assertEqual(412.3, self._df.ix[0].amount)

        # new tick data
        data['UpdateTime'] = '09:31:02'
        data['LastPrice'] = 10.1
        data['Volume'] = 300
        data['Turnover'] = 555.3

        self._api.onRtnDepthMarketData(data)

        self.assertEqual(2, len(self._df))
        self.assertEqual(10.1, self._df.ix[1].price)
        self.assertEqual(555.3, self._df.ix[1].amount)

    def test_onRtnDepthMarketData_With_Invalid_TickData(self):
        data = dict()
        data['InstrumentID'] = self._instrument
        data['UpdateTime'] = '09:31:00'
        data['LastPrice'] = 10.0
        data['Volume'] = 200
        data['Turnover'] = 412.3

        data['PreClosePrice'] = 10.0

        self._api.onRtnDepthMarketData(data)
        self.assertEqual(1, len(self._df))

        # new tick data with older time
        data['UpdateTime'] = '09:30:50'
        data['LastPrice'] = 10.1
        data['Volume'] = 300
        data['Turnover'] = 555.3
        self._api.onRtnDepthMarketData(data)
        self.assertEqual(1, len(self._df))
        self.assertTrue(self._logger.warn.called)

        # price is higher than pre_close * 1.1
        data['UpdateTime'] = '09:31:50'
        data['LastPrice'] = 12.0
        data['Volume'] = 300
        data['Turnover'] = 555.3
        self._api.onRtnDepthMarketData(data)
        self.assertEqual(1, len(self._df))
        self.assertTrue(self._logger.warn.called)

        # price is lower than pre_close * 0.9
        data['UpdateTime'] = '09:31:50'
        data['LastPrice'] = 8.0
        data['Volume'] = 300
        data['Turnover'] = 555.3
        self._api.onRtnDepthMarketData(data)
        self.assertEqual(1, len(self._df))
        self.assertTrue(self._logger.warn.called)

    def test_onRtnDepthMarketData_With_Invalid_DataContent(self):
        data = dict()
        data['InstrumentID'] = self._instrument
        data['UpdateTime'] = '09:31:00'
        data['LastPriceXXXXX'] = 10.0 # invalid dict data
        data['Volume'] = 200
        data['Turnover'] = 412.3

        data['PreClosePrice'] = 10.0

        self._api.onRtnDepthMarketData(data)

        self.assertEqual(0, len(self._df))

        # logger called check
        self.assertTrue(self._logger.error.called)

        data['InstrumentID'] = 'NonExist'
        self._api.onRtnDepthMarketData(data)

        self.assertEqual(0, len(self._df))

        # logger called check
        self.assertTrue(self._logger.error.called)




