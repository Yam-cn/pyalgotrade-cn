#coding:utf-8

import os

from vnctptd import TdApi
from ctpDataType import defineDict

from pyalgotrade.broker import Order
from pyalgotrade.logger import getLogger


class EventType(object):
    ON_LOGIN = 1
    ON_LOGOUT = 2
    ON_ORDER_ACCEPTED = 3
    ON_ORDER_ACTION = 4
    ON_TRADE = 5
    ON_ORDER = 6
    ON_TRADE_ERROR = 7
    ON_ORDER_ERROR = 8
    ON_QUERY_ORDER = 9
    ON_QUERY_TRADE = 10
    ON_QUERY_POSITION = 11
    ON_QUERY_ACCOUNT = 12
    ON_QUERY_INSTRUMENT = 13


########################################################################
class CTPTdApi(TdApi):
    """CTP交易API实现"""
    
    #----------------------------------------------------------------------
    def __init__(self, msg_queue):
        """API对象的初始化函数"""
        super(CTPTdApi, self).__init__()
        
        self.reqID = 0              # 操作请求编号
        self.orderRef = 0           # 订单编号
        
        self.connectionStatus = False       # 连接状态
        self.loginStatus = False            # 登录状态
        
        self.userID = None          # 账号
        self.password = None        # 密码
        self.brokerID = None        # 经纪商代码
        self.address = None         # 服务器地址
        
        self.frontID = None            # 前置机编号
        self.sessionID = None          # 会话编号
        
        self.__msg_queue= msg_queue
        self.__oders = set()
        
        self._logger = getLogger('CTP')
        
    
    #----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        self.connectionStatus = True
        
        self._logger.info('CTP trading connected')
        
        self.login()
    
    #----------------------------------------------------------------------
    def onFrontDisconnected(self, n):
        """服务器断开"""
        self.connectionStatus = False
        self.loginStatus = False

        self._logger.info('CTP trading disconnected')

    #----------------------------------------------------------------------
    def onHeartBeatWarning(self, n):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspAuthenticate(self, data, error, n, last):
        """"""
        if error['ErrorID'] == 0:
            pass
        
        else:
            self._logger.error({'error_id': error['ErrorID']})
            
        
    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        # 如果登录成功，推送日志信息
        
        if error['ErrorID'] == 0:
            self.frontID = data['FrontID']
            self.sessionID = data['SessionID']
            self.loginStatus = True

            self._logger.info('CTP trading login successful')
            
            # 确认结算信息
            req = {}
            req['BrokerID'] = self.brokerID
            req['InvestorID'] = self.userID
            self.reqID += 1
            self.reqSettlementInfoConfirm(req, self.reqID)
            
        # 否则，推送错误信息
        else:
            self._logger.error({'error_id':error['ErrorID']})
            
    #----------------------------------------------------------------------
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        # 如果登出成功，推送日志信息
        if error['ErrorID'] == 0:
            self.loginStatus = False

            self._logger.info(u'logout successful')
            
        # 否则，推送错误信息
        else:
            self._logger.error({'error_id':error['ErrorID']})
            
    #----------------------------------------------------------------------
    def onRspUserPasswordUpdate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspTradingAccountPasswordUpdate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspOrderInsert(self, data, error, n, last):
        """ order insert return """
        pass
            

    #----------------------------------------------------------------------
    def onRspParkedOrderInsert(self, data, error, n, last):
        """"""
        pass
    
    
    #----------------------------------------------------------------------
    def onRspParkedOrderAction(self, data, error, n, last):
        """"""
        pass
    
    
    #----------------------------------------------------------------------
    def onRspOrderAction(self, data, error, n, last):
        """modify order"""
        if error['ErrorID'] == 0:
            msg = {'event_type': EventType.ON_ORDER_ACTION}
            msg['order_id'] = data["OrderRef"]
            self.__msg_queue.put(msg)
        else:
            self._logger.error({'error_id': error['ErrorID']})
            
        
    #----------------------------------------------------------------------
    def onRspQueryMaxOrderVolume(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspSettlementInfoConfirm(self, data, error, n, last):
        """确认结算信息回报"""
        
        if error['ErrorID'] == 0:
            msg = {}
            msg['event_type'] = EventType.ON_LOGIN
            self.__msg_queue.put(msg)
        else:
            self._logger.error({'error_id': error['ErrorID']})
        
        
    #----------------------------------------------------------------------
    def onRspRemoveParkedOrder(self, data, error, n, last):
        """"""
        pass
    
    
    #----------------------------------------------------------------------
    def onRspRemoveParkedOrderAction(self, data, error, n, last):
        """"""
        pass
    
    
    #----------------------------------------------------------------------
    def onRspExecOrderInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspExecOrderAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspForQuoteInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspLockInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQuoteInsert(self, data, error, n, last):
        """"""
        print data
    
    #----------------------------------------------------------------------
    def onRspQuoteAction(self, data, error, n, last):
        """"""
        print data
        
    #----------------------------------------------------------------------
    def onRspCombActionInsert(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    ##TODO: return message is null, might be a bug in vnctptd.cpp
    def onRspQryOrder(self, data, error, n, last):
        """"""
        data['if_last'] = last
        self.__msg_queue.put(data)
    
    #----------------------------------------------------------------------
    ##TODO: return message is null, might be a bug in vnctptd.cpp
    def onRspQryTrade(self, data, error, n, last):
        """"""
        data['if_last'] = last
        self.__msg_queue.put(data)
    
    #----------------------------------------------------------------------
    ##TODO: 
    def onRspQryInvestorPosition(self, data, error, n, last):
        """持仓查询回报"""
        #print data
        if error['ErrorID'] == 0:
            msg = {'event_type': EventType.ON_QUERY_POSITION}
            msg['instrument_id'] = data['InstrumentID']
            msg['exchange_id'] = data['ExchangeID']
            msg['direction'] = data['PosiDirection']
            msg['open_volume'] = data['OpenVolume']
            msg['close_volume'] = data['CloseVolume']
            msg['frozen_margin'] = data['FrozenMargin']
            msg['pre_margin'] = data['PreMargin']
            msg['exchange_margin'] = data['ExchangeMargin']
            msg['position_profit'] = data["PositionProfit"]
            msg['close_profit'] = data['CloseProfit']
            msg['commission'] = data["Commission"]
            msg['pre_settlement_price'] = data['PreSettlementPrice']
            msg['settlement_price'] = data['SettlementPrice']
            msg['use_margin'] = data['UseMargin']
            msg['position'] = data['Position']
            msg['pre_position'] = data['YdPosition']
            msg['open_cost'] = data['OpenCost']
            msg['position_cost'] = data['PositionCost']
            msg['if_last'] = last
            self.__msg_queue.put(msg)
            
        else:
            self._logger.error({'error_id': error['ErrorID']})
    
    #----------------------------------------------------------------------
    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        #print data
        if error['ErrorID'] == 0:
            msg = {'event_type': EventType.ON_QUERY_ACCOUNT}
            
            msg['cash_available'] = data['Available']
            msg['cash_frozen'] = data['FrozenCash']
            msg['mortgage'] = data['Mortgage']
            msg['balance'] = data['Balance']
            msg['margin'] = data["CurrMargin"]
            msg['position_profit'] = data["PositionProfit"]
            msg['pre_margin'] = data['PreMargin']
            msg['trading_day'] = data['TradingDay']
            msg['exchange_margin'] = data['ExchangeMargin']
            msg['pre_deposit'] = data['PreDeposit']
            msg['pre_balance'] = data['PreBalance']
            msg['curr_margin'] = data['CurrMargin']
            msg['close_profit'] = data['CloseProfit']
            msg['if_last'] = last
            self.__msg_queue.put(msg)
            
        else:
            self._logger.error({'error_id': error['ErrorID']})
        

    #----------------------------------------------------------------------
    def onRspQryInvestor(self, data, error, n, last):
        """投资者查询回报"""
        pass
        
    #----------------------------------------------------------------------
    def onRspQryTradingCode(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInstrumentMarginRate(self, data, error, n, last):
        """"""
        pass
        
    #----------------------------------------------------------------------
    def onRspQryInstrumentCommissionRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchange(self, data, error, n, last):
        """"""
        pass
        
    #----------------------------------------------------------------------
    def onRspQryProduct(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInstrument(self, data, error, n, last):
        """合约查询回报"""
        if error['ErrorID'] == 0:
            ret = {}
            ret['instrument_id'] = data['InstrumentID']
            ret['exchange_id'] = data['ExchangeID']
            ret['product_id'] = data['ProductID']
            ret['is_trading'] = data['IsTrading']
            ret['expire_date'] = data['ExpireDate']
            ret['price_tick'] = data['PriceTick']
            ret['max_market_order_volume'] = data['MaxMarketOrderVolume']
            ret['min_market_order_volume'] = data['MinMarketOrderVolume']
            ret['max_limit_order_volume'] = data['MaxLimitOrderVolume']
            ret['min_limit_order_volume'] = data['MinLimitOrderVolume']
            ret['position_date_type'] = data['PositionDateType']
            ret['position_type'] = data['PositionType']
            ret['volume_multiple'] = data['VolumeMultiple']
            ret['underlying_multiple'] = data['UnderlyingMultiple']
            ret['product_class'] = data['ProductClass']
            ret['if_last'] = last

            data['if_last'] = last
            self.__msg_queue.put(data)
        else:
            self._logger.error({'error_id': error['ErrorID']})
        

    #----------------------------------------------------------------------
    def onRspQryDepthMarketData(self, data, error, n, last):
        """"""
        pass
        
    #----------------------------------------------------------------------
    def onRspQrySettlementInfo(self, data, error, n, last):
        """查询结算信息回报"""
        if error['ErrorID'] == 0:
            pass
            #self._server.onAccount(data)
            
        else:
            self._logger.error({'error_id': error['ErrorID']})
    
    #----------------------------------------------------------------------
    def onRspQryTransferBank(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryNotice(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQrySettlementInfoConfirm(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorPositionCombineDetail(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryCFMMCTradingAccountKey(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryEWarrantOffset(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorProductGroupMargin(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeMarginRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeMarginRateAdjust(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExchangeRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQrySecAgentACIDMap(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryProductExchRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryProductGroup(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryOptionInstrTradeCost(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryOptionInstrCommRate(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryExecOrder(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryForQuote(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryQuote(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryLock(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryLockPosition(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryInvestorLevel(self, data, error, n, last):
        """"""
        pass

    #----------------------------------------------------------------------
    def onRspQryExecFreeze(self, data, error, n, last):
        """"""
        pass

    #----------------------------------------------------------------------
    def onRspQryCombInstrumentGuard(self, data, error, n, last):
        """"""
        pass

    #----------------------------------------------------------------------
    def onRspQryCombAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryTransferSerial(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryAccountregister(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspError(self, error, n, last):
        """错误回报"""
        if error['ErrorID'] == 0:
            pass
            #self._server.onAccount(data)
            
        else:
            pass
            #self._logger.error({'error_id': error['ErrorID'], 'msg':error['ErrorMsg']})
        
    #----------------------------------------------------------------------
    def onRtnOrder(self, data):
        """order return"""    
        #print data
        # update order ref for manual order
        newref = data['OrderRef']
        self.orderRef = max(self.orderRef, int(newref))
        
        if self.orderRef in self.__oders:
            msg = {'event_type': EventType.ON_ORDER_ACCEPTED}
            msg['order_id'] = data["OrderRef"]
            self.__msg_queue.put(msg)
        else:
            print ('unrecognized order, orderRef: %d'%self.orderRef)
        
        
    #----------------------------------------------------------------------
    def onRtnTrade(self, data):
        """trade return"""
        print data
        if int(data["OrderRef"]) in self.__oders:
            msg = {'event_type': EventType.ON_TRADE}
            msg['order_id'] = data["OrderRef"]
            msg['trade_type'] = data['TradeType']
            msg['volume'] = data['Volume']
            msg['trade_id'] = data['OrderSysID']
            msg['price'] = data['Price']
            msg['instrument_id'] = data['InstrumentID']
            msg['exchange_id'] = data['ExchangeID']
            #msg['commision'] = data['Commision']
            
            msg['datetime'] = data['TradeDate'] + ' ' + data['TradeTime']
            
            msg['direction'] = data['Direction']
            msg['offset'] = data['OffsetFlag']
            self.__msg_queue.put(msg)
        else:
            #self._logger.info('trade return for unrecognized order, orderRef: %d'%self.orderRef)
            print ('unrecognized trade, orderRef: %d'%self.orderRef)
        

    #----------------------------------------------------------------------
    ##TODO:
    def onErrRtnOrderInsert(self, data, error):
        """发单错误回报（交易所）"""
        pass
    
    
    #----------------------------------------------------------------------
    ##TODO:
    def onErrRtnOrderAction(self, data, error):
        """撤单错误回报（交易所）"""
        pass
        
    
    #----------------------------------------------------------------------
    def onRtnInstrumentStatus(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnTradingNotice(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnErrorConditionalOrder(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnExecOrder(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnExecOrderInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnExecOrderAction(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnForQuoteInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnQuote(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQuoteInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQuoteAction(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnCFMMCTradingAccountToken(self, data):
        """"""
        pass

    #----------------------------------------------------------------------
    def onRtnLock(self, data):
        """"""
        pass

    #----------------------------------------------------------------------
    def onErrRtnLockInsert(self, data, error):
        """"""
        pass

    #----------------------------------------------------------------------
    def onRtnCombAction(self, data):
        """"""
        pass

    #----------------------------------------------------------------------
    def onErrRtnCombActionInsert(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnForQuoteRsp(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryContractBank(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryParkedOrder(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryParkedOrderAction(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryTradingNotice(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryBrokerTradingParams(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQryBrokerTradingAlgos(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQueryCFMMCTradingAccountToken(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromBankToFutureByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromFutureToBankByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromBankToFutureByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnFromFutureToBankByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFutureManual(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFutureManual(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnQueryBankBalanceByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnBankToFutureByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnFutureToBankByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnRepealBankToFutureByFutureManual(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnRepealFutureToBankByFutureManual(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onErrRtnQueryBankBalanceByFuture(self, data, error):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromBankToFutureByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnRepealFromFutureToBankByFuture(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspFromBankToFutureByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspFromFutureToBankByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRspQueryBankAccountMoneyByFuture(self, data, error, n, last):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnOpenAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnCancelAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def onRtnChangeAccountByBank(self, data):
        """"""
        pass
    
    #----------------------------------------------------------------------
    def connect(self, userID, password, brokerID, address):
        """初始化连接"""
        self.userID = userID                # 账号
        self.password = password            # 密码
        self.brokerID = brokerID            # 经纪商代码
        self.address = address              # 服务器地址
        
        # 如果尚未建立服务器连接，则进行连接
        if not self.connectionStatus:
            # 创建C++环境中的API对象，这里传入的参数是需要用来保存.con文件的文件夹路径
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tdconnection')
            if not os.path.exists(path):
                os.makedirs(path)
            self.createFtdcTraderApi(path +'/')

            # 从上次收到的续传
            self.subscribePrivateTopic(0)
            self.subscribePublicTopic(0)

            self.registerFront(self.address)
            
            # 初始化连接，成功会调用onFrontConnected
            self.init()
            
        # 若已经连接但尚未登录，则进行登录
        else:
            if not self.loginStatus:
                self.login()  
                
                
    
    #----------------------------------------------------------------------
    def login(self):
        """连接服务器"""
        # 如果填入了用户名密码等，则登录
        
        if self.userID and self.password and self.brokerID:
            req = dict()
            req['UserID'] = self.userID
            req['Password'] = self.password
            req['BrokerID'] = self.brokerID
            self.reqID += 1
            self.reqUserLogin(req, self.reqID)  
            
        
    #----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户"""
        self.reqID += 1
        req = {}
        #req['BrokerID'] = self.brokerID
        #req['InvestorID'] = self.userID
        self.reqQryTradingAccount(req, self.reqID)
        
    #----------------------------------------------------------------------
    def qryTrade(self):
        'query orders filled'
        self.reqID += 1
        req = {}
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        self.reqQryTrade(req, self.reqID)
    
    
    #----------------------------------------------------------------------
    def qryOrder(self):
        'query orders accepted'
        self.reqID += 1
        req = {}
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        self.reqQryOrder(req, self.reqID)
        
        
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        self.reqID += 1
        req = {}
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID
        self.reqQryInvestorPosition(req, self.reqID)
        
        # return for future server getting all of positions
        return self.reqID
        
        
    #----------------------------------------------------------------------
    def qryInstrument(self):
        """ """
        self.reqID += 1
        req = dict()
        self.reqQryInstrument(req, self.reqID)
        
        # return for future server getting all of positions
        return self.reqID
        
    #----------------------------------------------------------------------
    def sendOrder(self, symbol, action, price, volume):
        """Send Order
        Args:
            symbol: str, 'IF1610'
            action: int, Pyalgotrade.broker.Order.Action
            price: float,  3225.2
            volume: int, 2
        """
        self.reqID += 1
        self.orderRef += 1
        
        req = dict()
        
        if action == Order.Action.BUY:
            req['Direction'] = defineDict['THOST_FTDC_D_Buy']
            req['CombOffsetFlag'] = defineDict['THOST_FTDC_OF_Open']
        elif action == Order.Action.BUY_TO_COVER:
            req['Direction'] = defineDict['THOST_FTDC_D_Buy']
            req['CombOffsetFlag'] = defineDict['THOST_FTDC_OF_CloseToday']
        elif action == Order.Action.SELL:
            req['Direction'] = defineDict['THOST_FTDC_D_Sell']
            req['CombOffsetFlag'] = defineDict['THOST_FTDC_OF_CloseToday']
        elif action == Order.Action.SELL_SHORT:
            req['Direction'] = defineDict['THOST_FTDC_D_Sell']
            req['CombOffsetFlag'] = defineDict['THOST_FTDC_OF_Open']
            
        
        req['InstrumentID'] = symbol
        req['LimitPrice'] = price
        req['VolumeTotalOriginal'] = volume
        
        req['OrderPriceType'] = defineDict['THOST_FTDC_OPT_LimitPrice'] ##use only limited order
        
        req['OrderRef'] = str(self.orderRef)
        req['InvestorID'] = self.userID
        req['UserID'] = self.userID
        req['BrokerID'] = self.brokerID
        
        req['CombHedgeFlag'] = defineDict['THOST_FTDC_HF_Speculation']       # 投机单
        req['ContingentCondition'] = defineDict['THOST_FTDC_CC_Immediately'] # 立即发单
        req['ForceCloseReason'] = defineDict['THOST_FTDC_FCC_NotForceClose'] # 非强平
        req['IsAutoSuspend'] = 0                                             # 非自动挂起
        req['TimeCondition'] = defineDict['THOST_FTDC_TC_GFD']               # 今日有效
        req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']              # 任意成交量
        req['MinVolume'] = 1                                                 # 最小成交量为1
        
        
        self.reqOrderInsert(req, self.reqID)
        self.__oders.add(self.orderRef)
        #print 111111
        self._logger.debug('insert new order:%s'%req)
        
        return str(self.orderRef)
    
    #----------------------------------------------------------------------
    def cancelOrder(self, instrument, orderID):
        """撤单"""
        self.reqID += 1
        
        req = {}

        # 使用 frontID, sessionID, orderID三元组
        req['InstrumentID'] = instrument
        # req['ExchangeID'] = 'DCE'
        req['OrderRef'] = orderID
        req['FrontID'] = self.frontID
        req['SessionID'] = self.sessionID
        
        req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
        req['BrokerID'] = self.brokerID
        req['InvestorID'] = self.userID

        self.reqOrderAction(req, self.reqID)
        
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.exit()
        
        
    def getLogger(self):
        return self._logger
        

    
if __name__ == '__main__':
    pass
    #test_qry(10)
    #test_order(10)
    #account = load_account()
            
        
        
        
        
        
        
    

        