# coding:utf-8
# Copyright 2011-2016 ZackZK
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
import os


#import sys
#import codecs
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)
#sys.stderr = codecs.getwriter('utf8')(sys.stderr)

from vnctpmd import MdApi

#----------------------------------------------------------------------
def print_dict(d):
    """打印API收到的字典，该函数主要用于开发时的debug"""
    print '-'*60
    l = d.keys()
    l.sort()
    for key in l:
        print key, ':', d[key]


def valid_tick_data(this_time, pre_close, price, last_time):
        if last_time is not None and this_time < last_time:
            if this_time[:2] == '00' and last_time[:2] == '23':  # 行情跨天, 23点跳转到0点
                return True
            else:
                return False

        return float(pre_close) * 0.9 <= float(price) <= float(pre_close) * 1.1

########################################################################
class CTPMdApi(MdApi):
    """
    登陆 login
    订阅合约 subscribe
    """

    #----------------------------------------------------------------------
    def __init__(self, instruments, ticksDf, lock, logger):
        """
        API对象的初始化函数
        """
        super(CTPMdApi, self).__init__()


        # 请求编号，由api负责管理
        self.__reqid = 0

        # 以下变量用于实现连接和重连后的自动登陆
        self.__userid = ''
        self.__password = ''
        self.__brokerid = ''

        if not isinstance(instruments, list):
            raise Exception("identifiers must be a list")

        self.__instruments = instruments
        self.__ticksDf = ticksDf
        self.__lock = lock
        self.__logger = logger

        # 以下集合用于重连后自动订阅之前已订阅的合约，使用集合为了防止重复
        self.__setSubscribed = set()


        # 初始化.con文件的保存目录为\mdconnection，注意这个目录必须已存在，否则会报错
        path = os.path.dirname(os.path.abspath(__file__)) + '\\mdconnection\\'
        if not os.path.exists(path):
            os.makedirs(path)

        self.createFtdcMdApi(path)

    #----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        # 如果用户已经填入了用户名等等，则自动尝试连接
        if self.__userid or True:
            req = {}
            req['UserID'] = self.__userid
            req['Password'] = self.__password
            req['BrokerID'] = self.__brokerid
            self.__reqid = self.__reqid + 1
            self.reqUserLogin(req, self.__reqid)

    #----------------------------------------------------------------------
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print u'行情服务器连接断开'

    #----------------------------------------------------------------------
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        # 因为API的心跳报警比较常被触发，且与API工作关系不大，因此选择忽略
        pass

    #----------------------------------------------------------------------
    def onRspError(self, error, n, last):
        """错误回报"""

        log = u'行情错误回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')
        print log

    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""

        if error['ErrorID'] == 0:
            log = u'行情服务器登陆成功'
        else:
            log = u'登陆回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')

        print log

        ## 登录成功后进行订阅
        for instrument in self.__instruments:
            self.subscribe(instrument)

    #----------------------------------------------------------------------
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""

        if error['ErrorID'] == 0:
            log = u'行情服务器登出成功'
        else:
            log = u'登出回报，错误代码：' + unicode(error['ErrorID']) + u',' + u'错误信息：' + error['ErrorMsg'].decode('gbk')

        print log

    #----------------------------------------------------------------------
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        # 通常不在乎订阅错误，选择忽略
        pass

    #----------------------------------------------------------------------
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        # 同上
        pass

    #----------------------------------------------------------------------
    def onRtnDepthMarketData(self, data):
        """行情推送"""
        instrument = data['InstrumentID']

        # print_dict(data)

        if instrument not in self.__instruments:
            self.__logger.error(u'合约', instrument, '没有订阅')
            return

        try:
            time = data['UpdateTime']
            price = data['LastPrice']
            volume = data['Volume']
            amount = data['Turnover']
            pre_close = data['PreClosePrice']

            with self.__lock:
                df = self.__ticksDf[instrument]

                # print df

                last_quotation_time = None if len(df) == 0 else df.ix[len(df)-1].time

                if valid_tick_data(time, pre_close, price, last_quotation_time):
                    df.loc[len(df)] = [time, price, volume, amount]
                else:
                    self.__logger.warn(u'行情数据错误', data)

        except Exception, e:
            self.__logger.error(e)

    #----------------------------------------------------------------------
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅期权询价"""
        pass

    #----------------------------------------------------------------------
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订期权询价"""
        pass

    #----------------------------------------------------------------------
    def onRtnForQuoteRsp(self, data):
        """期权询价推送"""
        pass

    #----------------------------------------------------------------------
    def login(self, address, userid, password, brokerid):
        """连接服务器"""
        self.__userid = userid
        self.__password = password
        self.__brokerid = brokerid

        # 注册服务器地址
        self.registerFront(address)




        # 初始化连接，成功会调用onFrontConnected
        self.init()


    #----------------------------------------------------------------------
    def subscribe(self, instrumentid):
        """订阅合约"""
        self.subscribeMarketData(instrumentid)

        self.__setSubscribed.add(instrumentid)

if __name__ == "__main__":
    from time import sleep
    while True:
        sleep(1)

