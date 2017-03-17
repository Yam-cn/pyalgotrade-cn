from openft.open_quant_context import *
import sys

# Examples for use the python functions
#
def _example_stock_quote(quote_ctx):
    stock_code_list = ["US.AAPL", "HK.00700", "SZ.000001"]

    # subscribe "QUOTE"
    for stk_code in stock_code_list:
        ret_status, ret_data = quote_ctx.subscribe(stk_code, "QUOTE")
        if ret_status != RET_OK:
            print("%s %s: %s" % (stk_code, "QUOTE", ret_data))
            exit()

    ret_status, ret_data = quote_ctx.query_subscription()

    if ret_status == RET_ERROR:
        print(ret_status)
        exit()

    print(ret_data)

    ret_status, ret_data = quote_ctx.get_stock_quote(stock_code_list)
    if ret_status == RET_ERROR:
        print(ret_data)
        exit()
    quote_table = ret_data

    print("QUOTE_TABLE")
    print(quote_table)


def _example_cur_kline(quote_ctx):
    # subscribe Kline
    stock_code_list = ["US.AAPL", "HK.00700", "SZ.000001"]
    sub_type_list = ["K_1M", "K_5M", "K_15M", "K_30M", "K_60M", "K_DAY", "K_WEEK", "K_MON"]

    for code in stock_code_list:
        for sub_type in sub_type_list:
            ret_status, ret_data = quote_ctx.subscribe(code, sub_type)
            if ret_status != RET_OK:
                print("%s %s: %s" % (code, sub_type, ret_data))
                exit()

    ret_status, ret_data = quote_ctx.query_subscription()

    if ret_status == RET_ERROR:
        print(ret_data)
        exit()

    print(ret_data)

    for code in stock_code_list:
        for ktype in ["K_DAY", "K_1M", "K_5M"]:
            ret_code, ret_data = quote_ctx.get_cur_kline(code, 5, ktype)
            if ret_code == RET_ERROR:
                print(code, ktype, ret_data)
                exit()
            kline_table = ret_data
            print("%s KLINE %s" % (code, ktype))
            print(kline_table)
            print("\n\n")


def _example_rt_ticker(quote_ctx):
    stock_code_list = ["US.AAPL", "HK.00700", "SZ.000001", "SH.601318"]

    # subscribe "TICKER"
    for stk_code in stock_code_list:
        ret_status, ret_data = quote_ctx.subscribe(stk_code, "TICKER")
        if ret_status != RET_OK:
            print("%s %s: %s" % (stk_code, "TICKER", ret_data))
            exit()

    for stk_code in stock_code_list:
        ret_status, ret_data = quote_ctx.get_rt_ticker(stk_code, 10)
        if ret_status == RET_ERROR:
            print(stk_code, ret_data)
            exit()
        print("%s TICKER" % stk_code)
        print(ret_data)
        print("\n\n")


def _example_order_book(quote_ctx):
    stock_code_list = ["US.AAPL", "HK.00700", "SZ.000001", "SH.601318"]

    # subscribe "ORDER_BOOK"
    for stk_code in stock_code_list:
        ret_status, ret_data = quote_ctx.subscribe(stk_code, "ORDER_BOOK")
        if ret_status != RET_OK:
            print("%s %s: %s" % (stk_code, "ORDER_BOOK", ret_data))
            exit()

    for stk_code in stock_code_list:
        ret_status, ret_data = quote_ctx.get_order_book(stk_code)
        if ret_status == RET_ERROR:
            print(stk_code, ret_data)
            exit()
        print("%s ORDER_BOOK" % stk_code)
        print(ret_data)
        print("\n\n")


def _example_get_trade_days(quote_ctx):
    ret_status, ret_data = quote_ctx.get_trading_days("US", "2017-01-01", "2017-01-18")
    if ret_status == RET_ERROR:
        print(ret_data)
        exit()
    print("TRADING DAYS")
    for x in ret_data:
        print(x)


def _example_stock_basic(quote_ctx):
    ret_status, ret_data = quote_ctx.get_stock_basicinfo("US", "STOCK")
    if ret_status == RET_ERROR:
        print(ret_data)
        exit()
    print("stock_basic")
    print(ret_data)


class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("StockQuoteTest ", content)
        return RET_OK, content


class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(OrderBookTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("OrderBookTest", content)
        return RET_OK, content


class CurKlineTest(CurKlineHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(CurKlineTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("CurKlineTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("CurKlineTest", content)
        return RET_OK, content


class TickerTest(TickerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(TickerTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("TickerTest", content)
        return RET_OK, content


if __name__ == "__main__":

    #quote_context = OpenQuoteContext(host='127.0.0.1', async_port=11111)
    quote_context = OpenQuoteContext(host='119.29.141.202', async_port=11111)

    #quote_context.set_handler(StockQuoteTest())
    #quote_context.set_handler(OrderBookTest())


    quote_context.set_handler(CurKlineTest())
    #quote_context.set_handler(TickerTest())
    quote_context.start()
    quote_context.subscribe('HK.00700', "K_1M", push=True)
    
    
'''
    _example_stock_quote(quote_context)
    _example_cur_kline(quote_context)
    _example_rt_ticker(quote_context)
    _example_order_book(quote_context)
    _example_get_trade_days(quote_context)
    _example_stock_basic(quote_context)
'''
    
