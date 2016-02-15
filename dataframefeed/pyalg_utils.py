# -*- coding: utf-8 -*-
"""
Created on Mon Dec 07 21:37:31 2015

@author: Administrator
"""
from pyalgotrade.stratanalyzer import returns,sharpe,drawdown,trades
from datetime import datetime
import pandas as pd 
import json
import numpy as np
#返回某一策略对象的数据集  ,无getSet函数，只能手写      
class dataSet():
    def __init__(self,myStrategy):
        self.__myStrategy = myStrategy
        self.returnsAnalyzer = returns.Returns()
        self.sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.drawdownAnalyzer = drawdown.DrawDown()   
        self.tradeAyalyzer = trades.Trades()
        
        myStrategy.attachAnalyzer(self.returnsAnalyzer)
        myStrategy.attachAnalyzer(self.sharpeRatioAnalyzer)
        myStrategy.attachAnalyzer(self.drawdownAnalyzer)
        myStrategy.attachAnalyzer(self.tradeAyalyzer)
     
    #获取基本数据，价格等原始数据不在此处
    def getDefault(self):
        __returns = self.getReturns()  #收益率，长序列，array
        __cumulativeReturns = self.getCumulativeReturns()  #累计收益率，长序列，array
        __sharpRatio = self.getSharpeRatio()
        __maxDrawDown = self.getMaxDrawDown() #最大回撤
        __tradeInfo = self.getInfo()  #交易信息
        return{"returns":__returns,"cumulativeReturns":__cumulativeReturns,"sharpRatio":__sharpRatio,"maxDrawDown":__maxDrawDown,"tradeInfo":__tradeInfo}
        
        
    def getInfo(self):
        return self.__myStrategy.getInfo()
    def getTimeSeries(self):
        return self.__myStrategy.getDateTimeSeries()
    def getCumulativeReturns(self):
        return  change_type_toArray(self.returnsAnalyzer.getCumulativeReturns(),timeSeries = self.getTimeSeries()) #累计收益率,没有时间  ，dataSeries
    def getReturns(self):
        return change_type_toArray(self.returnsAnalyzer.getReturns(),timeSeries = self.getTimeSeries())  #收益率  ，dataSeries
    def getSharpeRatio(self):
        return self.sharpeRatioAnalyzer.getSharpeRatio(0.05) #夏普比率，参数为无风险利率 ，int
    def getLongestDrawDownDuration(self):
        return self.drawdownAnalyzer.getLongestDrawDownDuration()  #最大回撤久期 int
    def getMaxDrawDown(self):
        return self.drawdownAnalyzer.getMaxDrawDown() #最大回撤 int
    def getCount(self):
        return self.tradeAyalyzer.getCount() #交易笔数 int
    def getProfitableCount(self):
        return self.tradeAyalyzer.getProfitableCount()  #盈利笔数 int
    def getUnprofitableCount(self):
        return self.tradeAyalyzer.getUnprofitableCount() #未盈利笔数 int
    def getEvenCount(self):
        return self.tradeAyalyzer.getEvenCount() # 盈利为零的交易  int
    def getAll(self):       #pandas 格式，可使用to_json ,回报额
        info = self.getInfo()
        info = info[['date','instrument','id']][info['action']==3]
        info['All'] = self.tradeAyalyzer.getAll()        
        return info  #每笔交易的盈利、损失  dataFrame
    def getProfits(self):
        all = self.getAll()
        return all[all["All"]>0]# 每笔交易盈利 dataFrame
    def getLosses(self):
        all = self.getAll()
        return all[all["All"]<0]# 每笔交易盈利 dataFrame
    def getAllReturns(self):   
        info = self.getInfo()
        info = info[['date','instrument','id']][info['action']==3]
        info['AllReturn'] = self.tradeAyalyzer.getAllReturns()       
        return info  # 每笔交易回报率 ，pandas
    def getPositiveReturns(self):
        allReturn = self.getAllReturns()
        return allReturn[allReturn["AllReturn"]>0]# 每笔交易盈利 dataFrame
    def getNegativeReturns(self):
        allReturn = self.getAllReturns()
        return allReturn[allReturn["AllReturn"]<0]# 每笔交易盈利 dataFrame
    def getCommissionsForAllTrades(self):
        return self.tradeAyalyzer.getCommissionsForAllTrades() #Returns a numpy.array with the commissions for each trade.
    def getCommissionsForProfitableTrades(self):
        return self.tradeAyalyzer.getCommissionsForProfitableTrades()
    def getCommissionsForUnprofitableTrades(self):
        return self.tradeAyalyzer.getCommissionsForUnprofitableTrades()
    def getCommissionsForEvenTrades(self):
        return self.tradeAyalyzer.getCommissionsForEvenTrades()
        
#将dataSeries格式转换为array格式,无序
def change_type_toArray(data,timeSeries = None):
    
    i=0;
    result = []
    date_time = data.getDateTimes()  #返回dateTime格式
    while(i < len(data)):
        if timeSeries is None:
            if date_time[1] is None:
                result.append([i,data.__getitem__(i)])
            else:   
                result.append([date_time[i],data.__getitem__(i)])  #只找到该方法，挨个取出 ,若使用Str格式：.strftime('%Y-%m-%d')
        else:
            if type(timeSeries)== np.ndarray:
                result.append([timeSeries[i][0],data.__getitem__(i)]) #一番折腾 时间为datetime 64 格式，无法转换，求解决QQ；657959571
                #print datetime.utcfromtimestamp(timeSeries[i][0].astype(int))
            else:
                result.append([timeSeries[i],data.__getitem__(i)])  #只找到该方法，挨个取出
            #print timeSeries[i].strftime('%Y-%m-%d'),data.__getitem__(i) 
        i+=1
        #print result 
    return  np.array(result).reshape((len(result),2))
    
    
