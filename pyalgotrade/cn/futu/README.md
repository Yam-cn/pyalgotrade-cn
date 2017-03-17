---

##富途API简介
富途开放API开源项目可以满足 富途用户 使用富途牛牛软件进行量化投资。主要的功能如下：

1. 行情接口：美股、港股以及A股实时行情。具体权限和用户的富途牛牛行情权限保持一致。
2. 交易接口： 美股、港股的下单、查询持仓等。
3. 接口格式：Python接口、Json协议接口。

开源项目地址： https://github.com/FutunnOpen/OpenQuant

富途开放API群 `108534288`

富途API使用时要安装专门的富途牛牛客户端软件（到108534288群文件中下载），使用时程序要打开客户端，
监听127.0.0.1 1111端口才能接收到行情数据。

为了让大家能够快速体验富途API和方便调试，腾讯云上部署了体验环境可以访问行情接口:  ip =119.29.141.202,  port = 11111 , 可不用安装客户端直接体验。但是，使用云地址，会增大网络时延，不如客户端版本稳定，以及不能下载更多的历史数据。

##使用示例介绍
本示例只提供python版本的API，和pyalgotrade框架结合，实现历史数据回测和实时实盘数据回测。以下几个文件需要重点关注。

### pyalgotrade-cn\pyalgotrade\cn\futu\openft
是富途API的文件夹，包括了全部API接口，可以和pyalgotrade框架结合或单独使用。

###pyalgotrade-cn\pyalgotrade\cn\futu\barfeed.py
用富途open api的推送接口，写的获取k线数据文件。和pyalgotrade框架结合使用。

###pyalgotrade-cn\pyalgotrade\cn\futu\sample.py
是富途API的示例文件，可单独运行，不依赖pyalgotrade框架。具体参看main函数里例子的使用，或者加入QQ群询问。

OpenQuoteContext函数是初始话函数，需要绑定监听的ip和端口。目前默认绑定的是云ip，能够不安装客户端马上体验。

quote_context.set_handler函数，是使用push接口前，必须要调用的异步注册函数，参数是回调类，需要实现on_recv_rsp函数，具体参考源码或[项目地址](https://github.com/FutunnOpen/OpenQuant)

quote_context.subscribe 注册函数，需要获取哪些股票的数据，要在获取前进行订阅，否则会收不到数据。

###pyalgotrade-cn\stratlib\doubleMA_futu.py
使用富途API拉取k线接口，实现双均线策略的示例，直接运行该文件，即可看到0700股票，在2016-06-01到2017-06-01期间的盈亏情况。

先使用富途api下载港股00700股票，到本地的histdata文件夹中，保存为csv文件；

然后使用pyalgotrade.cn框架，加载数据，利用已有的双均线策略进行回测。

###pyalgotrade-cn\stratlib\thrSMA_live_futu.py
使用富途API实现的三均线策略，实时拉取港股00700股票k线数据，可直接运行查看。

启动时先下载20根k线，补充数据，然后准备好push接口，等服务器有数据推送时，获取k线数据，传到pyalgotrade框架进行回测处理。

## tips
以上只是简单示例，更多富途API使用方法和文档，请参考[项目地址](https://github.com/FutunnOpen/OpenQuant)，或加群讨论。

示例只是简单展示结合pyalgotrade，如果想更深入，请阅读pyalgotrade文档，或和群友讨论。


---
## 富途客户端下载及交流方式

富途开放API群 108534288

意见反馈地址 https://github.com/FutunnOpen/OpenQuant/issues