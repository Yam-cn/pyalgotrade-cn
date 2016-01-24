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
from pandas import DataFrame

from pyalgotrade.tushare.barfeed import TuSharePollingThread

class TestTuSharePollingThread(TestCase):
    def test_get_tushare_tick_data(self):
        self.fail()


class TestTuSharePollingThread(TestCase):
    def test_valid_tick_data_with_right_timestamp(self):
        stock_id = '000001'
        thread = TuSharePollingThread([stock_id])
        data_list = [[u'10.00', u'9.00', u'1000', u'2000', u'14:00:01']]
        columns = ['pre_close', 'price', 'volume', 'amount', 'time']
        df = DataFrame(data_list, columns=columns)

        self.assertTrue(thread.valid_tick_data(stock_id, df.ix[0]))

        df.ix[0].time = u'14:00:02'
        self.assertTrue(thread.valid_tick_data(stock_id, df.ix[0]))

        df.ix[0].time = u'14:00:00'
        self.assertFalse(thread.valid_tick_data(stock_id, df.ix[0]))

    def test_valid_tick_data_with_right_price(self):
        stock_id = '000001'
        thread = TuSharePollingThread([stock_id])

        data_list = [[u'10.00', u'10.00', u'1000', u'2000', u'14:00:01']]
        columns = ['pre_close', 'price', 'volume', 'amount', 'time']
        df = DataFrame(data_list, columns=columns)
        self.assertTrue(thread.valid_tick_data(stock_id, df.ix[0]))

        # price > pre_close * 1.1
        df.ix[0].price = u'11.01'
        df.ix[0].time = '14:00:03'
        self.assertFalse(thread.valid_tick_data(stock_id, df.ix[0]))

        # price < pre_close * 0.9
        df.ix[0].price = u'8.90'
        df.ix[0].time = '14:00:04'
        self.assertFalse(thread.valid_tick_data(stock_id, df.ix[0]))

