## 文档说明
该文件夹内，采用富途科技的api获取行情数据，进行回测。

`openft`文件夹，`sample.py`是富途open api的文件，用于拉取行情、交易等功能，具体参考 **[项目主页](https://github.com/FutunnOpen/OpenQuant) **

`barfeed.py` 用富途open api的推送接口，写的获取k线数据文件。

具体的使用示例，请参考 `pyalgotrade-cn\stratlib` 文件夹下的 `thrSMA_live_futu.py` 和 `doubleMA_futu.py` 策略示例文件。

`thrSMA_live_futu.py` 实时行情的三均线策略测试, 采用futu的push api，不用程序循环拉取，服务器有数据才push到本地，更稳定，减少计算资源。

`doubleMA_futu.py` 展示了如何使用富途open api进行下载历史k线，然后进行回测双均线策略的使用方法。历史k线下载到histdata文件夹内的csv文件。


futu api使用时要安装富途牛牛客户端软件，监听127.0.0.1 1111端口才能接收到行情，
如果想快速体验，腾讯云上部署了体验环境可以访问行情接口:  ip =119.29.141.202,  port = 11111 , 可不用安装客户端直接体验。

详细的使用方法请参考futu官方github和群。

---
## 富途客户端下载及交流方式

富途开放API群 108534288
http://www.futunn.com
https://github.com/FutunnOpen/OpenQuant/issues
