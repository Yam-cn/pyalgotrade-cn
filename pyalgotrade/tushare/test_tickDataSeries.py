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
from pyalgotrade.tushare.barfeed import TickDataSeries
from pyalgotrade import bar
from pyalgotrade.tushare.barfeed import build_bar


class TestBuild_bar(TestCase):
    def test_build_bar(self):
        ds = TickDataSeries()
        ds.append(u'1', u'11', u'111', '14:55:00')
        ds.append(u'5', u'55', u'555', '14:55:03')
        ds.append(u'3', u'33', u'333', '14:55:06')

        period_bar = build_bar('14:56:00', ds)

        self.assertEqual(period_bar.getOpen(), 1)
        self.assertEqual(period_bar.getHigh(), 5)
        self.assertEqual(period_bar.getLow(), 1)
        self.assertEqual(period_bar.getClose(), 3)
        self.assertEqual(period_bar.getVolume(), 99)
        self.assertEqual(period_bar.getAmount(), 999)

    def test_basic_build_bar(self):
        ds = TickDataSeries()
        ds.append(u'1', u'11', u'111', '14:55:00')

        period_bar = build_bar('14:56:00', ds)

        self.assertEqual(period_bar.getOpen(), 1)
        self.assertEqual(period_bar.getHigh(), 1)
        self.assertEqual(period_bar.getLow(), 1)
        self.assertEqual(period_bar.getClose(), 1)
        self.assertEqual(period_bar.getVolume(), 11)
        self.assertEqual(period_bar.getAmount(), 111)


class TestTickDataSeries(TestCase):

    def test_reset(self):
        ticks = TickDataSeries()
        ticks.append(1, 1 , 1, '14:55:00')
        ticks.reset()
        self.assertEqual(len(ticks.getPriceDS()), 0)
        self.assertEqual(len(ticks.getAmountDS()), 0)
        self.assertEqual(len(ticks.getVolumeDS()), 0)
        self.assertEqual(len(ticks.getDateTimes()), 0)

    def test_append(self):
        ticks = TickDataSeries()

        ticks.append(10.0, 1000, 999.9, '2015-12-17 14:55:00')
        self.assertEqual(ticks.getPriceDS()[0], 10.0)
        self.assertEqual(ticks.getAmountDS()[0], 999.9)
        self.assertEqual(ticks.getVolumeDS()[0], 1000)

    def test_empty(self):
        ticks = TickDataSeries()
        self.assertTrue(ticks.empty())

        ticks.append(10.0, 1000, 999.9, '2015-12-17 14:55:00')

        self.assertFalse(ticks.empty())

