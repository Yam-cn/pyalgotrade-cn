#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 23:36:25 2016

@author: James
"""

from pyalgotrade.cn.CTP.api import CTPTdApi
from pyalgotrade.broker import Order

def print_dict(idict):
    for key in idict:
        print key, idict[key]


def test_qry(timeout):
    import time
    import Queue
    
    address = "tcp://180.168.146.187:10000"
    userid = "052677"
    password = "4925453"
    brokerid = "9999"
    
    msg_queue = Queue.Queue()
    api = CTPTdApi.CTPTdApi(msg_queue)
    logger = api.getLogger()
    
    print '----------------------------------------------'
    print 'test login'
    api.connect(userid, password, brokerid, address)
    while True:
        #print api.loginStatus
        if api.loginStatus:
            print 'login successfull'
            break
    
    time.sleep(1)
    print '----------------------------------------------'
    print 'test qryAccount'
    api.qryAccount()
    try:
        msg = msg_queue.get(True, timeout)
        print msg
    except Queue.Empty:
        logger.debug('qryAccount timeout')
        
        
    time.sleep(1)
    print '----------------------------------------------'
    print 'test qryPosition'
    api.qryPosition()
    try:
        msg = []
        while True:
            msg.append(msg_queue.get(True, timeout))
            if msg[-1]['if_last'] == 1:
                print 'got %d position'%len(msg)
                print msg[-1]
                break
    except Queue.Empty:
        logger.debug('qryPosition timeout')       
        
    
    time.sleep(1)
    print '----------------------------------------------'
    print 'test qryOrder'
    api.qryOrder()
    try:
        msg = []
        while True:
            msg.append(msg_queue.get(True, timeout))
            if msg[-1]['if_last'] == 1:
                print 'got %d order'%len(msg)
                print msg[-1]
                break
    except Queue.Empty:
        logger.debug('qryOrder timeout')    
            
    time.sleep(1)        
    print '----------------------------------------------'
    print 'test qryTrade'
    api.qryTrade()
    try:
        msg = []
        while True:
            msg.append(msg_queue.get(True, timeout))
            if msg[-1]['if_last'] == 1:
                print 'got %d trade'%len(msg)
                #print_dict(msg[-1])
                break
    except Queue.Empty:
        logger.debug('qryTrade timeout')   
          
        
    time.sleep(1)
    print '----------------------------------------------'
    print 'test qryInstrument'
    api.qryInstrument()
    try:
        msg = []
        while True:
            msg.append(msg_queue.get(True, timeout))
            if msg[-1]['if_last'] == 1:
                print 'got %d instruments'%len(msg)
                print_dict(msg[-1])
    except Queue.Empty:
        logger.debug('qryTrade timeout')        
        
    
    while True:
        try:
            pass
        except KeyboardInterrupt:
            return
            
def test_order(timeout):
    symbol = 'ag1702'
    action = Order.Action.BUY
    price = 3950
    volume = 1
    
    import Queue
    import time
    
    account_info = load_account()
    address = "tcp://" + account_info['address'] + ":" + account_info['port']
    userid = account_info['userid']
    password = account_info['password']
    brokerid = account_info['brokerid']
    
    msg_queue = Queue.Queue()
    api = CTPTdApi.CTPTdApi(msg_queue)
    logger = api.getLogger()
    
    print '----------------------------------------------'
    print 'test login'
    api.connect(userid, password, brokerid, address)
    while True:
        #print api.loginStatus
        if api.loginStatus:
            print 'login successfull'
            break
        
             
    time.sleep(1)
    print '----------------------------------------------'
    print 'test sendOrder'
    order_ref = api.sendOrder(symbol, action, price, volume)
    try:
        msg = msg_queue.get(True, timeout)
        print msg
    except Queue.Empty:
        logger.debug('sendOrder timeout')    
        
        
    time.sleep(5)
    print '----------------------------------------------'
    print 'test cancelOrder'
    api.cancelOrder(symbol, order_ref)
    try:
        msg = msg_queue.get(True, timeout)
        print msg
    except Queue.Empty:
        logger.debug('cancelOrder timeout')   
        
        
    while True:
        try:
            pass
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    pass
    test_qry(10)
    #test_order(10)
    #account = load_account()