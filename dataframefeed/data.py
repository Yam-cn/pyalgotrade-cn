# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 11:04:32 2015

@author: lenovo
"""
from itertools import izip
#import sys
import constant as ct
import pylab as plt
import pandas as pd
import tushare as ts
import numpy as np
import time,os
from pandas import DataFrame
#reload(sys)
#sys.setdefaultencoding('utf-8')
#code为全部，code_inuse为起止日期完备的数据
def save_data():
    dat = ts.get_industry_classified()
    dat = dat.drop_duplicates('code')  
    dat.to_csv('d:/data/code.csv',encoding='gbk')
    inuse = []
    
    i = 0
    for code in dat['code'].values:
        i+= 1
        print i,code
        try:
            _data_ = ts.get_hist_data(code,end=ct._MIDDLE_)  #默认取3年，code为str，start无效的,start 和end若当天有数据则全都取
            if _data_ is not None:
                _data_.to_csv('d:/data/%s.csv'%code,encoding='gbk')
                if _data_.index[0] in ct._start_range and _data_.index[-1] in ct._end_range:                          #筛选一次代码，使用头尾都包含的代码
                    inuse.append(code)
        except IOError: 
            pass    #不行的话还是continue           
    #print len(inuse)
    _df_inuse = DataFrame(inuse,columns={'code'})
    _df_inuse.to_csv('d:/data/code_inuse.csv',encoding='gbk')

#从网络中更新数据,code 必须为str，dat中的为int
def refresh_data(_start_ ='2015-08-01',_end_ = ct._TODAY_):
    dat = pd.read_csv('d:/data/code.csv',index_col=0,encoding='gbk')
    inuse = pd.read_csv('d:/data/code_inuse.csv',index_col=0,parse_dates=[0],encoding='gbk')
    new_inuse = []
    
    i=0
    for code in dat['code'].values:
        i+= 1
        print i,code
        try:
            _data_ = ts.get_hist_data(str(code),start=_start_,end=_end_)  #默认取3年，start 8-1包括
            filename = 'd:/data/%s.csv'%code
            if _data_ is not None and _data_.size != 0:
                if os.path.exists(filename):
                    _data_.to_csv(filename, mode='a', header=None,encoding='gbk')
                else:
                    _data_.to_csv(filename,encoding='gbk')
                if code in inuse['code'].values and _data_.index[0] in pd.date_range(start=_start_,periods=7) and _data_.index[-1] in pd.date_range(end=_end_,periods=7):                          #筛选一次代码，使用头尾都包含的代码
                    new_inuse.append(code)  
        except IOError: 
            pass    #不行的话还是continue           
    #print len(inuse)
    _df_inuse = DataFrame(new_inuse,columns={'code'})
    _df_inuse.to_csv('d:/data/code_new_inuse.csv',encoding='gbk')
                
                
def read_data():      
    dat = pd.read_csv('d:/data/code.csv',index_col=0,encoding='gbk')
    dic = {}
    
    i = 0
    for code in dat['code'].values:
        i+= 1
        print i,code
        try:
            df = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')  #parse_dates直接转换数据类型，不用再重新狗再累   
            if df is not None:
                dic[code] = df
        except IOError: 
            pass    #不行的话还是continue
    return dic

#仅适用数据头尾完备的code    
def get_universe():
    try:
        dat = pd.read_csv('d:/data/code_inuse.csv',index_col=0,parse_dates=[0],encoding='gbk')
    except Exception: 
        dat = ts.get_industry_classified()
    dat = dat.drop_duplicates('code')                                                   #去除重复code
    return dat['code'].values 

#    
def get_data(code):
    try:
        dat = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')  #parse_dates直接转换数据类型，不用再重新狗再累 
    except Exception:
        dat = None
    return dat
def get_macd(df):
    _columns_ = ['EMA_12','EMA_26','DIFF','MACD','BAR']
    a = np.zeros(len(df)*5).reshape(len(df),5) #也可以EMA_12 = [0 for i in range(len(df))]
    a[-1][0] =  df['close'][0]    #EMA_12
    a[-1][1] =  df['close'][0]
    
    for i in range(len(df)):
        a[i][0] = a[i-1][0]*11/13+df['close'][i]*2/13  #EMA_12       
        a[i][1] = a[i-1][1]*25/27+df['close'][i]*2/27 #EMA_26
        a[i][2] =  a[i][0]-a[i][1]  #DIFF
        a[i][3] = a[i-1][3]*8/10+a[i][2]*2/10 #MACD
        a[i][4]=2*(a[i][2]-a[i][3])
    return DataFrame(a,index = df.index,columns = _columns_) 

#df为原dataframe da为macd
def plt_macd(df,da):
    my_dfs = [df['open'], da['EMA_12'], da['EMA_26'], da['DIFF'], da['MACD'], da['BAR'],] # or in your case [ df,do]
    my_opts = [ {"color":"green", "linewidth":1.0, "linestyle":"-","label":"open"},
                {"color":"blue","linestyle":"-","label":"EMA_12"},
                {"color":"yellow","linestyle":"-","label":"EMA_26"},
                {"color":"black","linestyle":"-","label":"DIFF"},
                {"color":"red","linestyle":"-","label":"MACD"},
                {"color":"orange","linestyle":"-","label":"BAR"}]
    for d,opt in izip(my_dfs, my_opts):
        d.plot( **opt)
    plt.grid()
    plt.legend(loc=0)
    plt.show()  


#save_data()
#refresh_data()
#df = pd.read_csv('d:/data/600848.csv',index_col=0,parse_dates=[0],encoding='gbk') 
#da = get_macd(df) 
#plt_macd(df,da)
#_data_ = pd.read_csv('d:/data/600848.csv',index_col=0,encoding='gbk')  
#dic = read_data()
#_data_ = ts.get_hist_data('900901',start=ct._START_,end=ct._MIDDLE_)
#print _data_


def temp2():
    dat = pd.read_csv('d:/data/code.csv',index_col=0,encoding='gbk')
    inuse = []   
    i = 0
    for code in dat['code'].values:
        i+= 1
        print i,code
        try:
            _data_ = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')   #默认取3年，code为str，start无效的,start 和end若当天有数据则全都取
            if _data_ is not None:
                if _data_.index[0] in ct._start_range and _data_.index[-1] in ct._end_range:                          #筛选一次代码，使用头尾都包含的代码
                    inuse.append(code)
        except IOError: 
            pass    #不行的话还是continue           
    #print len(inuse)
    _df_inuse = DataFrame(inuse,columns={'code'})
    _df_inuse.to_csv('d:/data/code_inuse.csv',encoding='gbk')
def temp():
    dat = pd.read_csv('d:/data/code.csv',index_col=0,encoding='gbk')
    inuse = pd.read_csv('d:/data/code_inuse.csv',index_col=0,parse_dates=[0],encoding='gbk')
    new_inuse = []
        
    i=0
    for code in dat['code'].values:
            i+= 1
            #print i,code
            try:
                _data_ = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')  #默认取3年，start 8-1包括
                if code in inuse['code'].values and _data_.index[0] in pd.date_range(start=ct._START_,periods=7) and _data_.index[-1] in pd.date_range(end=ct._TODAY_,periods=7):                          #筛选一次代码，使用头尾都包含的代码
                   new_inuse.append(code)
                   
            except IOError: 
                pass    #不行的话还是continue           
        #print len(inuse)
    _df_inuse = DataFrame(new_inuse,columns={'code'})
    _df_inuse.to_csv('d:/data/code_new_inuse.csv',encoding='gbk')

#temp2() 
#重命名索引名，列名，将调整收盘价置为none
def change_type_to_yahoo():
    inuse = pd.read_csv('d:/data/code_inuse.csv',index_col=0,parse_dates=[0],encoding='gbk')               
    inuse.to_csv('d:/data2/code_inuse.csv',encoding='gbk')
    re_columns ={'high':'High','low':'Low','open':'Open','close':'Close','volume':'Volume','price_change':'Adj Close'}  
    i=0
    for code in inuse['code'].values:
        i+= 1
        print i,code
        _data_ = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')  #默认取3年，start 8-1包括
        _data_=_data_.rename(columns=re_columns)
        _data_.index.name = 'Date'
        _data_.to_csv('d:/data2/%s.csv'%code,columns=['Open','High','Low','Close','Volume','Adj Close'],date_format="%Y-%m-%d",encoding='gbk')
        
def get_beta(values1, values2):
    # http://statsmodels.sourceforge.net/stable/regression.html
    model = sm.OLS(values1, values2)
    results = model.fit()
    return results.params[0]
    value1=[0.5,1.0,1.5,2.0,2.5,3.0]
    value2=[1.75,2.45,3.81,4.80,7.00,8.60]
    print get_beta(value1,value2)
    
#选择下跌行情中天量成交和高换手率，后期加入小盘股等指标，scope 为近15日
#scope =15,看最近15天的情况，v_times 为当日成交量为前一日的倍数，t_percent为当日换手率
def bigVolume(scope=15,v_times=5,t_percent=20):
    inuse = pd.read_csv('d:/data/code_inuse.csv',index_col=0,parse_dates=[0],encoding='gbk')
    rs_list = []
    i=0
    for code in inuse['code'].values:
        try:
             _data_ = pd.read_csv('d:/data/%s.csv'%code,index_col=0,parse_dates=[0],encoding='gbk')   #默认取3年，code为str，start无效的,start 和end若当天有数据则全都取
             dd = (_data_['volume']/_data_['volume'].shift(1)>v_times) & (_data_['turnover']>t_percent)
             dd = dd & (_data_['close']<22)
             if dd[-scope:].any():
                 i+=1
                 if i<5:
                     _data_['close'].plot()
                 rs_list.append(code)
                 print i,code
        except IOError: 
             pass    #不行的话还是continue
#refresh_data()              
#change_type_to_yahoo()
bigVolume()
#_data_ = pd.read_csv('d:/data/600848.csv',index_col=0,parse_dates=[0],encoding='gbk')   #默认取3年，code为str，start无效的,start 和end若当天有数据则全都取
#_data_.plot() 
