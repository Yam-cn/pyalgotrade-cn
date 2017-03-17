# -*- coding: utf-8 -*-

import sys
import json
from datetime import datetime
from datetime import timedelta


'''
 parameter relation Mappings between PLS and Python programs
'''
mkt_map = {"HK": 1,
           "US": 2,
           "SH": 3,
           "SZ": 4,
           "HK_FUTURE": 6
           }
rev_mkt_map = {mkt_map[x]: x for x in mkt_map}


sec_type_map = {"STOCK": 3,
                "IDX": 6,
                "ETF": 4,
                "WARRANT": 5,
                "BOND": 1
                }
rev_sec_type_map = {sec_type_map[x]: x for x in sec_type_map}


subtype_map = {"TICKER": 4,
               "QUOTE":  1,
               "ORDER_BOOK": 2,
               "K_1M":    11,
               "K_5M":     7,
               "K_15M":    8,
               "K_30M":    9,
               "K_60M":   10,
               "K_DAY":    6,
               "K_WEEK":  12,
               "K_MON":   13
               }
rev_subtype_map = {subtype_map[x]: x for x in subtype_map}


ktype_map = {"K_1M":     1,
             "K_5M":     6,
             "K_15M":    7,
             "K_30M":    8,
             "K_60M":    9,
             "K_DAY":    2,
             "K_WEEK":   3,
             "K_MON":    4
             }

rev_ktype_map = {ktype_map[x]: x for x in ktype_map}

autype_map = {None: 0,
              "qfq": 1,
              "hfq": 2
              }

rev_autype_map = {autype_map[x]: x for x in autype_map}


ticker_direction = {"TT_BUY": 1,
                    "TT_SELL": 2,
                    "TT_NEUTRAL": 3
                    }

rev_ticker_direction = {ticker_direction[x]: x for x in ticker_direction}


RET_OK = 0
RET_ERROR = -1

ERROR_STR_PREFIX = 'ERROR. '


def check_date_str_format(s):
    try:
        _ = datetime.strptime(s, "%Y-%m-%d")
        return RET_OK, None
    except ValueError:
        err = sys.exc_info()[1]
        error_str = ERROR_STR_PREFIX + str(err)
        return RET_ERROR, error_str


def extract_pls_rsp(rsp_str):
    try:
        rsp = json.loads(rsp_str)
    except ValueError:
        err = sys.exc_info()[1]
        err_str = ERROR_STR_PREFIX + str(err)
        return RET_ERROR, err_str, None

    error_code = int(rsp['ErrCode'])

    if error_code != 0:
        error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
        return RET_ERROR, error_str, None

    if 'RetData' not in rsp:
        error_str = ERROR_STR_PREFIX + 'No ret data found in client rsp. Response: %s' % rsp
        return RET_ERROR, error_str, None

    return RET_OK, "", rsp


def normalize_date_format(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    ret = date_obj.strftime("%Y-%m-%d")
    return ret


def split_stock_str(stock_str):

    if isinstance(stock_str, str) is False:
        error_str = ERROR_STR_PREFIX + "value of stock_str is %s of type %s, and type %s is expected" \
                                       % (stock_str, type(stock_str), str(str))
        return RET_ERROR, error_str

    split_loc = stock_str.find(".")
    '''do not use the built-in split function in python.
    The built-in function cannot handle some stock strings correctly.
    for instance, US..DJI, where the dot . itself is a part of original code'''
    if 0 <= split_loc < len(stock_str) - 1 and stock_str[0:split_loc] in mkt_map:
        market_str = stock_str[0:split_loc]
        market_code = mkt_map[market_str]
        partial_stock_str = stock_str[split_loc+1:]
        return RET_OK, (market_code, partial_stock_str)

    else:

        error_str = ERROR_STR_PREFIX + "format of %s is wrong. (US.AAPL, HK.00700, SZ.000001)" % stock_str
        return RET_ERROR, error_str


def merge_stock_str(market, partial_stock_str):
    """
    :param market: market code
    :param partial_stock_str: original stock code string. i.e. "AAPL","00700", "000001"
    :return: unified representation of a stock code. i.e. "US.AAPL", "HK.00700", "SZ.000001"

    """

    market_str = rev_mkt_map[market]
    stock_str = '.'.join([market_str, partial_stock_str])
    return stock_str


def str2binary(s):
    """
    :param s: string content to be transformed to binary
    :return: binary
    """
    return s.encode('utf-8')


def binary2str(b):
    """

    :param b: binary content to be transformed to string
    :return: string
    """
    return b.decode('utf-8')


class TradeDayQuery:
    """
    Query Conversion for getting trading days.
    """
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, start_date=None, end_date=None):
        """
        Convert from user request for trading days to PLS request
        :param market:
        :param start_date:
        :param end_date:
        :return:  json string for request

        Example:

        ret,msg,content =  TradeDayQuery.pack_req("US", "2017-01-01", "2017-01-18")

        ret: 0
        msg: ""
        content:
        '{"Protocol": "1013", "Version": "1", "ReqParam": {"end_date": "2017-01-18",
        "Market": "2", "start_date": "2017-01-01"}}\r\n'

        """

        # '''Parameter check'''
        if market not in mkt_map:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in mkt_map]))
            return RET_ERROR, error_str, None

        if start_date is None:
            today = datetime.today()
            start = today - timedelta(days=365)

            start_date = start.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            today = datetime.today()
            end_date = today.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # pack to json
        mkt_str = str(mkt_map[market])
        req = {"Protocol": "1013",
               "Version": "1",
               "ReqParam": {"Market": mkt_str,
                            "start_date": start_date,
                            "end_date": end_date
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """
        Convert from PLS response to user response
        :param rsp_str:
        :return: trading day list

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1013","RetData":{"Market":"2",
        "TradeDateArr":["2017-01-17","2017-01-13","2017-01-12","2017-01-11",
        "2017-01-10","2017-01-09","2017-01-06","2017-01-05","2017-01-04",
        "2017-01-03"],"end_date":"2017-01-18","start_date":"2017-01-01"},"Version":"1"}\n\r\n\r\n'

         ret,msg,content = TradeDayQuery.unpack_rsp(rsp_str)

         ret : 0
         msg : ""
         content : ['2017-01-17',
                    '2017-01-13',
                    '2017-01-12',
                    '2017-01-11',
                    '2017-01-10',
                    '2017-01-09',
                    '2017-01-06',
                    '2017-01-05',
                    '2017-01-04',
                    '2017-01-03']

        """
        # response check and unpack response json to objects
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'TradeDateArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TradeDateArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_trading_day_list = rsp_data['TradeDateArr']

        if raw_trading_day_list is None or len(raw_trading_day_list) == 0:
            return RET_OK, "", []

        # convert to list format that we use
        trading_day_list = [normalize_date_format(x) for x in raw_trading_day_list]

        return RET_OK, "", trading_day_list


class StockBasicInfoQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, stock_type='STOCK'):
        """

        :param market:
        :param stock_type:
        :return: json string for request

        Example:
         ret,msg,content = StockBasicInfoQuery.pack_req("HK_FUTURE","IDX")

         ret : 0
         msg : ""
         content : '{"Protocol": "1014", "Version": "1", "ReqParam": {"Market": "6", "StockType": "6"}}\r\n'
        """
        if market not in mkt_map:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in mkt_map]))
            return RET_ERROR, error_str, None

        if stock_type not in sec_type_map:
            error_str = ERROR_STR_PREFIX + " stock_type is %s, which is not valid. (%s)" \
                                           % (stock_type, ",".join([x for x in sec_type_map]))
            return RET_ERROR, error_str, None

        mkt_str = str(mkt_map[market])
        stock_type_str = str(sec_type_map[stock_type])
        req = {"Protocol": "1014",
               "Version": "1",
               "ReqParam": {"Market": mkt_str,
                            "StockType": stock_type_str,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """

        :param rsp_str:
        :return: json string for request

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1014",
        "RetData":{"BasicInfoArr":
        [{"LotSize":"0","Name":"恒指当月期货","StockCode":"999010","StockID":"999010","StockType":"6"},
        {"LotSize":"0","Name":"恒指下月期货","StockCode":"999011","StockID":"999011","StockType":"6"}],
        "Market":"6"},"Version":"1"}\n\r\n\r\n'


         ret,msg,content = StockBasicInfoQuery.unpack_rsp(rsp_str)

        ret : 0
        msg : ""
        content : [{'code': 'HK_FUTURE.999010',
                    'lot_size': 0,
                    'name': '恒指当月期货',
                    'stock_type': 'IDX'},
                   {'code': 'HK_FUTURE.999011',
                    'lot_size': 0,
                    'name': '恒指下月期货',
                    'stock_type': 'IDX'}]

        """
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'BasicInfoArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find BasicInfoArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_basic_info_list = rsp_data["BasicInfoArr"]
        market = rsp_data["Market"]

        if raw_basic_info_list is None or len(raw_basic_info_list) == 0:
            return RET_OK, "", []

        basic_info_list = [{"code": merge_stock_str(int(market), record['StockCode']),
                            "name": record["Name"],
                            "lot_size": int(record["LotSize"]),
                            "stock_type": rev_sec_type_map[int(record["StockType"])]
                            }
                           for record in raw_basic_info_list]
        return RET_OK, "", basic_info_list


class MarketSnapshotQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """

        :param stock_list:
        :return:
        """
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {"Protocol": "1015",
               "Version": "1",
               "ReqParam": {"StockArr": [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "SnapshotArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SnapshotArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_snapshot_list = rsp_data["SnapshotArr"]

        if raw_snapshot_list is None or len(raw_snapshot_list) == 0:
            return RET_OK, "", []

        snapshot_list = [{'code': merge_stock_str(int(record['MarketType']), record['StockCode']),
                          'data_date': datetime.fromtimestamp(int(record['UpdateTime'])).strftime("%Y-%m-%d"),
                          'data_time': datetime.fromtimestamp(int(record['UpdateTime'])).strftime("%H:%M:%S"),
                          'last_price': float(record['NominalPrice'])/1000,
                          'open_price': float(record['OpenPrice'])/1000,
                          'high_price': float(record['HighestPrice'])/1000,
                          'low_price': float(record['LowestPrice'])/1000,
                          'prev_close_price': float(record['LastClose'])/1000,
                          'volume': int(record['SharesTraded']),
                          'turnover':  float(record['Turnover'])/1000,
                          'turnover_rate': float(record['TurnoverRatio'])/1000,
                          'suspension': True if int(record['SuspendFlag']) == 2 else False,
                          'listing_date': datetime.fromtimestamp(int(record['ListingDate'])).strftime("%Y-%m-%d")
                          }
                         for record in raw_snapshot_list if int(record['RetErrCode']) == 0]

        return RET_OK, "", snapshot_list


class HistoryKlineQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, start_date=None, end_date=None, ktype='K_DAY', autype='qfq'):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        # check date format
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # check k line type
        if ktype not in ktype_map:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in ktype_map]))
            return RET_ERROR, error_str, None

        if autype not in autype_map:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in autype_map]))
            return RET_ERROR, error_str, None

        req = {"Protocol": "1024",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
                            'StockCode': stock_code,
                            'start_date': start_date,
                            'end_date': end_date,
                            'KLType': str(ktype_map[ktype]),
                            'RehabType': str(autype_map[autype])
                            }
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "HistoryKLArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HistoryKLArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["HistoryKLArr"] is None or len(rsp_data["HistoryKLArr"]) == 0:
            return RET_OK, "", []

        raw_kline_list = rsp_data["HistoryKLArr"]
        price_base = 10**9
        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        kline_list = [{"code": stock_code,
                       "time_key": record['Time'],
                       "open": float(record['Open'])/price_base,
                       "high": float(record['High'])/price_base,
                       "low": float(record['Low'])/price_base,
                       "close": float(record['Close'])/price_base,
                       "volume": record['TDVol'],
                       "turnover": float(record['TDVal'])/1000
                       }
                      for record in raw_kline_list]

        return RET_OK, "", kline_list


class ExrightQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {"Protocol": "1025",
               "Version": "1",
               "ReqParam": {'StockArr': [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "ExRightInfoArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find ExRightInfoArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["ExRightInfoArr"] is None or len(rsp_data["ExRightInfoArr"]) == 0:
            return RET_OK, "", []

        get_val = (lambda x, y: float(y[x])/100000 if x in y else 0)
        raw_exr_list = rsp_data["ExRightInfoArr"]
        exr_list = [{'code': merge_stock_str(int(record['Market']), record['StockCode']),
                     'ex_div_date': record['ExDivDate'],
                     'split_ratio': get_val('SplitRatio', record),
                     'per_cash_div': get_val('PerCashDiv', record),
                     'per_share_div_ratio': get_val('PerShareDivRatio', record),
                     'per_share_trans_ratio': get_val('PerShareTransRatio', record),
                     'allotment_ratio': get_val(r'AllotmentRatio', record),
                     'allotment_price': get_val('AllotmentPrice', record),
                     'stk_spo_ratio': get_val('StkSpoRatio', record),
                     'stk_spo_price':  get_val('StkSpoPrice', record),
                     'forward_adj_factorA': get_val('ForwardAdjFactorA', record),
                     'forward_adj_factorB': get_val('ForwardAdjFactorB', record),
                     'backward_adj_factorA': get_val('BackwardAdjFactorA', record),
                     'backward_adj_factorB': get_val('BackwarAdjFactorB', record)
                     }
                    for record in raw_exr_list]

        return RET_OK, "", exr_list


class SubscriptionQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_subscribe_req(cls, stock_str, data_type):
        """
        :param stock_str:
        :param data_type:
        :return:
        """
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in subtype_map:
            subtype_str = ','.join([x for x in subtype_map])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = subtype_map[data_type]
        req = {"Protocol": "1005",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockSubType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_subscribe_rsp(cls, rsp_str):

        ret, msg, content = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        return RET_OK, "", None

    @classmethod
    def pack_unsubscribe_req(cls, stock_str, data_type):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in subtype_map:
            subtype_str = ','.join([x for x in subtype_map])
            error_str = ERROR_STR_PREFIX + 'data_type is %s, which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = subtype_map[data_type]

        req = {"Protocol": "1006",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockSubType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_unsubscribe_rsp(cls, rsp_str):
        ret, msg, content = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        return RET_OK, "", None

    @classmethod
    def pack_subscription_query_req(cls):
        req = {"Protocol": "1007",
               "Version": "1",
               "ReqParam": {}
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_subscription_query_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SubInfoArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TradeDateArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        subscription_table = {}

        raw_subscription_list = rsp_data['SubInfoArr']
        if raw_subscription_list is None or len(raw_subscription_list) == 0:
            return RET_OK, "", subscription_table

        subscription_list = [(merge_stock_str(int(x['Market']), x['StockCode']),
                              rev_subtype_map[int(x['StockSubType'])])
                             for x in raw_subscription_list]

        for stock_code_str, sub_type in subscription_list:
            if sub_type not in subscription_table:
                subscription_table[sub_type] = []
            subscription_table[sub_type].append(stock_code_str)

        return RET_OK, "", subscription_table

    @classmethod
    def pack_push_req(cls, stock_str, data_type):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in subtype_map:
            subtype_str = ','.join([x for x in subtype_map])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = subtype_map[data_type]
        req = {"Protocol": "1008",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockPushType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def pack_push_req(cls, stock_str, data_type):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in subtype_map:
            subtype_str = ','.join([x for x in subtype_map])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = subtype_map[data_type]
        req = {"Protocol": "1008",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockPushType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str


class StockQuoteQuery:
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """

        :param stock_list:
        :return:
        """
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {"Protocol": "1023",
               "Version": "1",
               "ReqParam": {'ReqArr': [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "SubSnapshotArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SubSnapshotArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_quote_list = rsp_data["SubSnapshotArr"]

        quote_list = [{'code': merge_stock_str(int(record['Market']), record['StockCode']),
                       'data_date': record['Date'],
                       'data_time': record['Time'],
                       'last_price': float(record['Cur'])/1000,
                       'open_price': float(record['Open'])/1000,
                       'high_price': float(record['High'])/1000,
                       'low_price': float(record['Low'])/1000,
                       'prev_close_price': float(record['LastClose'])/1000,
                       'volume': int(record['TDVol']),
                       'turnover':  float(record['TDVal'])/1000,
                       'turnover_rate': float(record['Turnover'])/1000,
                       'amplitude': float(record['Amplitude'])/1000,
                       'suspension': True if int(record['Suspension']) != 2 else False,
                       'listing_date': record['ListTime']
                       }
                      for record in raw_quote_list]

        return RET_OK, "", quote_list


class TickerQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, num=500):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, and the type shoud be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        req = {"Protocol": "1012",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
                            'StockCode': stock_code,
                            "Sequence": str(-1),
                            'Num': str(num)
                            }
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "TickerArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TickerArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_ticker_list = rsp_data["TickerArr"]
        if raw_ticker_list is None or len(raw_ticker_list) == 0:
            return RET_OK, "", []

        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        ticker_list = [{"stock_code": stock_code,
                        "time":  record['Time'],
                        "price": float(record['Price'])/1000,
                        "volume": record['Volume'],
                        "turnover": float(record['Turnover'])/1000,
                        "ticker_direction": rev_ticker_direction[int(record['Direction'])],
                        "sequence": int(record["Sequence"])
                        }
                       for record in raw_ticker_list]
        return RET_OK, "", ticker_list


class CurKlineQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, num, ktype='K_DAY', autype='qfq'):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if ktype not in ktype_map:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in ktype_map]))
            return RET_ERROR, error_str, None

        if autype not in autype_map:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in autype_map]))
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, which type shoud be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None

        req = {"Protocol": "1011",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
                            'StockCode': stock_code,
                            'Num': str(num),
                            'KLType': str(ktype_map[ktype]),
                            'RehabType': str(autype_map[autype])
                            }
               }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "KLDataArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find KLDataArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if "KLType" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find KLType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["KLDataArr"] is None or len(rsp_data["KLDataArr"]) == 0:
            return RET_OK, "", []

        k_type = rsp_data["KLType"]
        try:
            k_type = int(k_type)
            k_type = rev_ktype_map[k_type]
        except Exception:
            err = sys.exc_info()[1]
            error_str = ERROR_STR_PREFIX + str(err) + str(rsp_data["KLType"])
            return RET_ERROR, error_str, None

        raw_kline_list = rsp_data["KLDataArr"]
        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        kline_list = [{"code": stock_code,
                       "time_key": record['Time'],
                       "open": float(record['Open'])/1000,
                       "high": float(record['High'])/1000,
                       "low": float(record['Low'])/1000,
                       "close": float(record['Close'])/1000,
                       "volume": record['TDVol'],
                       "turnover": float(record['TDVal'])/1000,
                       "k_type": k_type
                       }
                      for record in raw_kline_list]

        return RET_OK, "", kline_list


class OrderBookQuery:

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str):
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        req = {"Protocol": "1002",
               "Version": "1",
               "ReqParam": {'Market': str(market_code), 'StockCode': stock_code, 'Num': str(10)}
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "GearArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find GearArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_book = rsp_data["GearArr"]
        stock_str = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])

        order_book = {'stock_code': stock_str, 'Ask': [], 'Bid': []}

        for record in raw_order_book:
            bid_record = (float(record['BuyPrice'])/1000, int(record['BuyVol']), int(record['BuyOrder']))
            ask_record = (float(record['SellPrice'])/1000, int(record['SellVol']), int(record['SellOrder']))

            order_book['Bid'].append(bid_record)
            order_book['Ask'].append(ask_record)

        return RET_OK, "", order_book

