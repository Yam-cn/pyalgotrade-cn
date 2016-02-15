# -*- coding: utf-8 -*-
"""
Created on Tue Oct 06 11:13:33 2015
turrle_test 提供三种数据加载方式：csv，dataFrame，sql(未完成直接方式，暂由dataFrame为桥)
dataFrame方式调用同目录util文件夹下的dataFrameBarfeed.py 和dataFramefeed.py
提供两种数据调取方式，一种为系统自带画图，另一种提供array方式各数据的接口，详见pyalg_utils.py
vwanp 提供组合管理示例
@author: lenovo
"""

from pyalgotrade import plotter
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import returns,sharpe,drawdown,trades
from datetime import datetime
from matplotlib.pyplot import plot 
from compiler.ast import flatten
import pyalg_test
import constant as ct
import pandas as pd 
import json
import pyalg_utils,data,data_sql
from utils import dataFramefeed

def turtle_test(load_type = 'csv',dataString = 'pyalg'):
    if load_type =='csv':
        #Load the yahoo feed from the CSV file
        feed = yahoofeed.Feed()
        feed.addBarsFromCSV("orcl", "D:/data2/600687.csv")
    elif load_type =='dataFrame':
        #从dataFrame中加载，
        dat = pd.read_csv('d:/data/600687.csv',index_col=0,encoding='gbk')
        feed = dataFramefeed.Feed()
        feed.addBarsFromDataFrame("orcl", dat)
    elif load_type == 'sql':
        #此处也是
        dat = data_sql.get_h_data('600848')
        feed = dataFramefeed.Feed()
        feed.addBarsFromDataFrame("orcl", dat)
    
    # Evaluate the strategy with the feed's bars.
    #myStrategy = pyalg_test.SMACrossOver(feed, "orcl", 20)
    myStrategy = pyalg_test.turtle(feed, "orcl",20,10)
    # Attach a returns analyzers to the strategy.
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    
    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy)
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())  
    
    if dataString =='pyalg_util':
        ds = pyalg_utils.dataSet(myStrategy)   #抽取交易数据集语句，若使用系统自带画图功能则不需要该项
    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())
    
    if dataString =='pyalg_util':
        rs = ds.getDefault()       #获取默认的交易信息，dic格式
        plot(rs["cumulativeReturns"][:,0],rs["cumulativeReturns"][:,1])  #简单作图示例
     
    plt.plot()

def vwap(plot):
    instrument = ["lenovo","mi"]
    vwapWindowSize = 5
    threshold = 0.01
    # Download the bars.
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("lenovo", "D:/data2/600687.csv")
    feed.addBarsFromCSV("mi", "D:/data2/600701.csv")

    strat = pyalg_test.VWAPMomentum(feed, instrument, vwapWindowSize, threshold)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        #plt.getPortfolioSubplot().addDataSeries("vwap", strat.getVWAP()[instrument[-1]])
    ds = pyalg_utils.dataSet(strat)   #抽取交易数据集语句，若使用系统自带画图功能则不需要该项
    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()
    
    rs = ds.getReturns()     #获取默认的交易信息，dic格式,可忽略  
    #for items in rs:
       # print items[0],items[1]

if __name__ == '__main__':
    #vwap(True)
    turtle_test()
