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
import pandas as pd
import datetime
from pyalgotrade.tushare.barfeed import get_trading_days


class TestGet_trading_days(TestCase):
    @mock.patch('pyalgotrade.tushare.barfeed.ts')
    def test_get_trading_days(self, mock_tushare):
        start_day = datetime.datetime(2015, 8, 8)

        data = [['2015-08-06', 10.0, 11.0, 10.5, 10.0], ['2015-08-07', 10.0, 11.0, 10.5, 10.0]]
        COLUMNS = ['date', 'open', 'high', 'close', 'low']
        df = pd.DataFrame(data, columns=COLUMNS)
        df = df.set_index('date')

        mock_tushare.get_hist_data.return_value = df

        trading_days = get_trading_days(start_day, 2)

        self.assertEqual(2015, trading_days[0].year)
        self.assertEqual(8, trading_days[0].month)
        self.assertEqual(6, trading_days[0].day)

        self.assertEqual(2015, trading_days[1].year)
        self.assertEqual(8, trading_days[1].month)
        self.assertEqual(7, trading_days[1].day)

    @mock.patch('pyalgotrade.tushare.barfeed.ts')
    def test_get_trading_days_with_one_holiday(self, mock_tushare):
        start_day = datetime.datetime(2015, 8, 10)

        data = [['2015-08-06', 10.0, 11.0, 10.5, 10.0], ['2015-08-07', 10.0, 11.0, 10.5, 10.0]]
        COLUMNS = ['date', 'open', 'high', 'close', 'low']
        df = pd.DataFrame(data, columns=COLUMNS)
        df = df.set_index('date')

        mock_tushare.get_hist_data.return_value = df

        trading_days = get_trading_days(start_day, 2)

        self.assertEqual(2015, trading_days[0].year)
        self.assertEqual(8, trading_days[0].month)
        self.assertEqual(6, trading_days[0].day)

        self.assertEqual(2015, trading_days[1].year)
        self.assertEqual(8, trading_days[1].month)
        self.assertEqual(7, trading_days[1].day)

    @mock.patch('pyalgotrade.tushare.barfeed.ts')
    def test_get_trading_days_with_two_holidays(self, mock_tushare):
        start_day = datetime.datetime(2015, 8, 18)

        data = [['2015-08-07', 10.0, 11.0, 10.5, 10.0], ['2015-08-10', 10.0, 11.0, 10.5, 10.0],
                ['2015-08-11', 10.0, 11.0, 10.5, 10.0], ['2015-08-12', 10.0, 11.0, 10.5, 10.0],
                ['2015-08-13', 10.0, 11.0, 10.5, 10.0], ['2015-08-14', 10.0, 11.0, 10.5, 10.0],
                ['2015-08-17', 10.0, 11.0, 10.5, 10.0]]
        COLUMNS = ['date', 'open', 'high', 'close', 'low']
        df = pd.DataFrame(data, columns=COLUMNS)
        df = df.set_index('date')

        mock_tushare.get_hist_data.return_value = df

        trading_days = get_trading_days(start_day, 7)

        self.assertEqual(7, len(trading_days))

        self.assertEqual(2015, trading_days[0].year)
        self.assertEqual(8, trading_days[0].month)
        self.assertEqual(7, trading_days[0].day)

        self.assertEqual(2015, trading_days[6].year)
        self.assertEqual(8, trading_days[6].month)
        self.assertEqual(17, trading_days[6].day)

