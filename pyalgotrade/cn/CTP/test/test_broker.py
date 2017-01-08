#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 23:47:55 2016

@author: chopchopjames
"""
from pyalgotrade.cn.CTP import livebroker
from pyalgotrade import broker

def test_limit_order():
    brk = livebroker.LiveBroker('052677')
    brk.start()
    order = brk.createLimitOrder(broker.Order.Action.BUY, 'ag1702', 4030, 1)
    brk.submitOrder(order)
    #brk.send
    
    pre_status = 0
    while True:
        if pre_status != order.getState():
            print 'order status: %d'%order.getState()
            pre_status = order.getState()
        brk.dispatch()
        
        if pre_status == order.State.FILLED:
            break
        
    
def test_cancel_order():
    brk = livebroker.LiveBroker('052677')
    brk.start()
    order = brk.createLimitOrder(broker.Order.Action.BUY, 'ag1702', 3950, 1)
    brk.submitOrder(order)
    #brk.send
    
    pre_status = 0
    cancel_count = 0
    while True:
        if pre_status != order.getState():
            print 'order status: %d'%order.getState()
            pre_status = order.getState()
        brk.dispatch()
        
        if pre_status == order.State.ACCEPTED and cancel_count < 1:
            import time
            time.sleep(5)
            brk.cancelOrder(order)
            cancel_count += 1
            
            
if __name__ == '__main__':
    #test_limit_order()
    test_cancel_order()    
            
            
            
            
            