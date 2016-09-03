### 2016-09-03 更新：
1. 合并所有本地化的模块到/cn文件夹中，方便大家使用和跟原版进行对比。
2. pyalgotrade本体升级为0.18.
3. 加入对tick行情结构的支持，见/stratlib/orderbook.py


Pyalgotrade-cn 在原版的基础上加入了A股历史行情回测，并整合了tushare提供实时行情。以便大家对自己的策略进行回测和模拟测试。

本次更新的内容：

 * 引入tushare实时行情
 * stratlib提供了两个经典策略(DT, Bollinger_bandit)

历史行情下载，提出需求，参加讨论，请加群：300349971


以下是原版的介绍：

PyAlgoTrade is an **event driven algorithmic trading** Python library. Although the initial focus
was on **backtesting**, **paper trading** is now possible using:

 * [Bitstamp](https://www.bitstamp.net/) for Bitcoins
 * [Xignite](https://www.xignite.com/) for stocks

and **live trading** is now possible using:

 * [Bitstamp](https://www.bitstamp.net/) for Bitcoins

To get started with PyAlgoTrade take a look at the [tutorial](http://gbeced.github.io/pyalgotrade/docs/v0.17/html/tutorial.html) and the [full documentation](http://gbeced.github.io/pyalgotrade/docs/v0.17/html/index.html).

Main Features
-------------

 * Event driven.
 * Supports Market, Limit, Stop and StopLimit orders.
 * Supports any type of time-series data in CSV format like Yahoo! Finance, Google Finance, Quandl and NinjaTrader.
 * [Xignite](https://www.xignite.com/) realtime feed.
 * Bitcoin trading support through [Bitstamp](https://www.bitstamp.net/).
 * Technical indicators and filters like SMA, WMA, EMA, RSI, Bollinger Bands, Hurst exponent and others.
 * Performance metrics like Sharpe ratio and drawdown analysis.
 * Handling Twitter events in realtime.
 * Event profiler.
 * TA-Lib integration.

Installation
------------

PyAlgoTrade is developed using Python 2.7 and depends on:

 * [NumPy and SciPy](http://numpy.scipy.org/).
 * [pytz](http://pytz.sourceforge.net/).
 * [dateutil](https://dateutil.readthedocs.org/en/latest/).
 * [requests](http://docs.python-requests.org/en/latest/).
 * [matplotlib](http://matplotlib.sourceforge.net/) for plotting support.
 * [ws4py](https://github.com/Lawouach/WebSocket-for-Python) for Bitstamp support.
 * [tornado](http://www.tornadoweb.org/en/stable/) for Bitstamp support.
 * [tweepy](https://github.com/tweepy/tweepy) for Twitter support.

You can install PyAlgoTrade using pip like this:

```
pip install pyalgotrade
```
