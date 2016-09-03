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
from pandas import DataFrame

from pyalgotrade import dataseries
from pyalgotrade.tushare.barfeed import TuShareLiveFeed


class TestTuShareLiveFeed(TestCase):
    @mock.patch('pyalgotrade.tushare.barfeed.is_holiday')
    @mock.patch('pyalgotrade.tushare.barfeed.ts')
    def test__fill_today_bars(self, mock_tushare, mock_is_holiday):
        data_list = [[u'09:33:45', 9.10, 100, 2000, 0.01],
                     [u'09:33:20', 9.20, 100, 2000, 0.01],
                     [u'09:33:00', 9.30, 100, 2000, 0.01],
                     [u'09:32:59', 9.40, 100, 10, 0.01],
                     [u'09:32:45', 9.01, 100, 100, 0.01],
                     [u'09:32:13', 9.02, 300, 1000, 0.01],
                     [u'09:31:58', 9.03, 300, 2000, 0.01],
                     [u'09:31:43', 8.94, 500, 2000, 0.01]
                     ]
        columns = ['time', 'price', 'volume', 'amount', 'change']
        df = DataFrame(data_list, columns=columns)

        mock_tushare.get_today_ticks.return_value = df

        mock_is_holiday.return_value = False

        liveFeed = TuShareLiveFeed(['000581'], 60, dataseries.DEFAULT_MAX_LEN, 0)
        #liveFeed.start()

        bars = liveFeed.getNextBars()
        self.assertEqual(bars['000581'].getHigh(), 9.03)
        self.assertEqual(bars['000581'].getVolume(), 800)

        bars = liveFeed.getNextBars()
        self.assertEqual(bars['000581'].getClose(), 9.40)
        self.assertEqual(bars['000581'].getAmount(), 1110)
        self.assertEqual(bars['000581'].getDateTime().strftime("%H:%M:%S"), "09:32:00")

        bars = liveFeed.getNextBars()
        self.assertEqual(bars['000581'].getOpen(), 9.30)

    @mock.patch('pyalgotrade.tushare.barfeed.is_holiday')
    @mock.patch('pyalgotrade.tushare.barfeed.get_trading_days')
    @mock.patch('pyalgotrade.tushare.barfeed.ts')
    def test__fill_history_bars(self, mock_tushare, mock_days, mock_is_holiday):
        data_list = [[u'09:33:45', 9.10, 100, 2000, 0.01],
                     [u'09:33:20', 9.20, 100, 2000, 0.01],
                     [u'09:33:00', 9.30, 100, 2000, 0.01],
                     [u'09:32:59', 9.40, 100, 10, 0.01],
                     [u'09:32:45', 9.01, 100, 100, 0.01],
                     [u'09:32:13', 9.02, 300, 1000, 0.01],
                     [u'09:31:58', 9.03, 300, 2000, 0.01],
                     [u'09:31:43', 8.94, 500, 2000, 0.01]
                     ]

        day1_data_list = [[u'11:00:58', 9.03, 300, 2000, 0.01],
                          [u'11:00:43', 8.94, 500, 2000, 0.01]
                          ]
        columns = ['time', 'price', 'volume', 'amount', 'change']

        df = DataFrame(data_list, columns=columns)
        mock_tushare.get_today_ticks.return_value = df

        day1_df = DataFrame(day1_data_list, columns=columns)

        day2_data_list = [[u'10:33:45', 9.10, 100, 2000, 0.01],
                          [u'10:33:20', 9.20, 100, 2000, 0.01],
                          [u'10:33:00', 9.30, 100, 2000, 0.01]
                          ]
        day2_df = DataFrame(day2_data_list, columns=columns)

        mock_tushare.get_tick_data.return_value = day2_df
        mock_is_holiday.return_value = False

        import datetime
        day1 = datetime.datetime(2015, 8, 8)
        mock_days.return_value = [day1]

        liveFeed = TuShareLiveFeed(['000581'], 60, dataseries.DEFAULT_MAX_LEN, 1)

        bars = liveFeed.getNextBars()
        self.assertEqual(bars['000581'].getHigh(), 9.30)
        self.assertEqual(bars['000581'].getVolume(), 300)

        bars = liveFeed.getNextBars()
        self.assertEqual(bars['000581'].getOpen(), 8.94)
        self.assertEqual(bars['000581'].getVolume(), 800)


