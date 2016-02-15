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
import sqlalchemy as sa 
from pandas import DataFrame
from sqlalchemy import create_engine
from datetime import datetime, timedelta
#reload(sys)
#sys.setdefaultencoding('utf-8')

def set_h_data(start = ct._START_,middle = ct._MIDDLE_,autype="qfq",index=False,retry_count = 3,pause=0):
    """
        获取历史交易信息存入数据库中，默认从1994-2015年。若不设定默认取最近一年，其他参数与tushare相同
        指数行情tushare其实可以查询，但未提供列表，因此自行构造
    Parameters
    ------
        
        
    return
    """
    _CODE_INDEX = pd.DataFrame({'code':['000001','399001','399006'],'name':['上证指数','深证指数','创业板指数'],'c_name':['指数','指数','指数']})
    code_index = _CODE_INDEX.set_index('code')
    dat = ts.get_industry_classified()
    dat = dat.drop_duplicates('code')
    
    engine = create_engine(ct._ENGINE_)
    dat.to_sql('code',engine,if_exists ='replace') #如果存在就覆盖表
    
    dat = dat.append(code_index)
    _time_= pd.period_range(start,middle,freq='Y')  #time[0] 为1994-12-31
    _start_ = start
    i = 0
    for code in dat['code'].values: 
        i+= 1
        if dat[dat['code']==code]['c_name'] is "指数":  #若为上证或深证指数。则设定index为True
            index = True
        for _end_ in _time_:
            _end_ = _end_.strftime('%Y-%m-%d')
            
            print i,code,_end_
            try:
                _data_ = ts.get_h_data(code,start=_start_,end=_end_,index=index,autype=autype,retry_count=retry_count,pause=pause) #两个日期之间的前复权数据 
                #_iterables_ = [[code],_data_.index] #无奈，选择multi——index，且需重新构造
                #_index_ = pd.MultiIndex.from_product(_iterables_, names=['code', 'date'])
                #_data_ = DataFrame(_data_, index= _index_,columns =_data_.columns)
                if _data_ is not None:                    
                    _data_['code'] =code
                    _data_.to_sql('h_data',engine,if_exists='append')
            except Exception,e:
                print e.args[0]
                pass    #不行的话还是continue           
            _start_ = _end_
            
def get_h_data(code):   
    engine = create_engine(ct._ENGINE_)
    return pd.read_sql(sa.text('SELECT * FROM h_data where code=:col1'), engine, params={'col1': code},parse_dates=['date'],index_col=['date'])

def set_hist_data(start = None,end = None,ktype = None,retry_count = 3,pause=0):
    """
        获取近三年交易信息存入数据库中，不同的ktype存入不同的表，参数与tushare相同
        None 即为取近三年
        若ktype = None ,则设定为全部
    Parameters
    ------
        
        
    return
    """
    engine = create_engine(ct._ENGINE_)
    dat =pd.read_sql_table('code', engine)
    dat =dat[dat['c_name']!='指数']['code'].values
    dat = dat.tolist()
    dat += ['sh','sz','hs300','sz50','zxb','cyb']
    i = 0
    if ktype is None:
        ktype = ['D','W','M','5','15','30','60']
    else:
        ktype = [ktype]
        
    for key_item in ktype:
        i+= 1
        for code in dat: 
            print i,code,key_item
            try:
                _data_ = ts.get_hist_data(code,start=start,end=end,ktype=key_item,retry_count=retry_count,pause=pause) #两个日期之间的前复权数据 
                if _data_ is not None:                    
                    _data_['code'] =code
                    _data_.to_sql('hist_data_%s'%key_item,engine,if_exists='append')
            except Exception,e:
                print e.args[0]
                pass    #不行的话还是continue          

def get_hist_data(code,ktype="D"):
    """
        获取数据库中全部的（hist）交易信息,默认取日线
    Parameters
    ------  
    return
    """
    engine = create_engine(ct._ENGINE_)
    return pd.read_sql(sa.text('SELECT * FROM "hist_data_%s" where code=:col1'%ktype), engine, params={'col1': code},parse_dates=['date'],index_col=['date'])

def set_realtime_quotes(code=['sh'],pause = 10):
    """
        获取当日所选股票代码的实时数据，code为股票代码列表，pause为每隔多少秒请求一次.从当前时间开始,未测试
        将数据存储到数据库中，若当前时间在9:00--15:00之间则实时获取并存入dic{code:dataFrame}中，否则进入睡眠状态
        目前睡眠，未考虑是否为交易日
        
    Parameters
    ------  
    return  list[DataFrame]
    """       
    engine = create_engine(ct._ENGINE_)
    curTime = datetime.now()
    startTime = curTime.replace(hour=9, minute=0, second=0, microsecond=0)
    endTime = curTime.replace(hour=15, minute=0, second=0, microsecond=0)
    delta_s = startTime - curTime
    delta_e = endTime - startTime
    if delta_s > timedelta(0, 0, 0):
        time.sleep(delta_s.total_seconds()) 
    elif delta_e <timedelta(0, 0, 0):
        time.sleep(delta_s.total_seconds()+86400)
    
    _data_ = {}
    for items in code:
        _data_[items] = DataFrame()
    while(curTime<endTime):
        for item in code: 
            df = ts.get_realtime_quotes(item) #Single stock symbol
            _data_[item].append(df)
        time.sleep(pause) 
        curTime = datetime.now() 
    for ite in code:
        _data_[ite].to_sql('realtime_data',engine,if_exists='append')
    return _data_
        
    
print get_hist_data('600051')     
 
def set_stock_basics():
    """
        获取股本信息存入数据库中
    Parameters
    ------
        
        
    return
    """
    dat = ts.get_stock_basics()
    engine = create_engine(ct._ENGINE_)
    dat.to_sql('stock_basics',engine,if_exists ='replace') 
    
    
