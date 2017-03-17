## 富途开放API简介

富途开放API开源项目可以满足 富途用户 使用富途牛牛软件进行量化投资。主要的功能如下：

1. 行情接口：美股、港股以及A股实时行情。具体权限和用户的富途牛牛行情权限保持一致。
2. 交易接口： 美股、港股的下单、查询持仓等。
3. 接口格式：Python接口、Json协议接口。

开源项目地址： https://github.com/FutunnOpen/OpenQuant

本文简介python接口的使用方式。

## 使用前准备

1. 到QQ群（108534288）的群文件中下载支持API的牛牛客户端。
    
    如果不安装客户端，需要连接云服务器ip使用，后面有介绍。
    
2. 安装python 2.7以上版本
3. 安装python的pandas的包

其中2和3两步可以直接安装anaconda一次解决，也可以直接进入QQ群（108534288）文件找anaconda包下载安装解决。


## API使用Quick start

具体例子参照sample.py文件，直接运行就能看到数据被拉取的效果。如果遇到'NoneType' object is not iterable问题，请忽略，不影响数据拉取。

### 1. 创建Context类

`OpenQuoteContext(host, async_port)`

这一步是基础，host填写要链接的服务地址，async_port是端口，如果本地打开了牛牛客户端（必须从QQ群内文件下载），则使用
quote_context = OpenQuoteContext(host='127.0.0.1', async_port=11111)创建；

如果为了快速看到API效果，可以使用quote_context = OpenQuoteContext(host='119.29.141.202', async_port=11111)链接远端云服务器ip。但是时延、稳定性不如安装客户端。

### 2. 订阅要查询的股票和类型

使用OpenQuoteContext的subscribe函数进行订阅，订阅成功后，才能接收或拉取要查询的股票信息。

例如：
subscribe('HK.00700', "K_1M", push=True)

第一个参数'HK.00700'表示要拉取的股票id，HK是市场，00700是股票的id。

K_1M表示拉取的是1分钟k线

push 为True表示服务器给push信息过来，为False表示要去服务器主动拉取数据。两种方法调用有差别。

### 3. 获取数据
### 3.1 Push方法
如果订阅采用push=True的参数，要调用OpenQuoteContext的set_handler函数，设置回调的类，在类里实现on_recv_rsp函数，收到数据后处理的方法。
然后再调用OpenQuoteContext的start()方法开始运行，准备接收数据。

### 3.2 主动拉取
如果订阅采用push=False的参数，要调用OpenQuoteContext的subscribe函数注册，成功后再根据需求，调用OpenQuoteContext的主动获取数据的接口。

具体请参考
https://github.com/FutunnOpen/OpenQuant/tree/master/%E5%BC%80%E6%94%BE%E6%8E%A5%E5%8F%A3/Python%E6%8E%A5%E5%8F%A3
中的文档文件。