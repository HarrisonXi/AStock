#新浪财经历史数据API

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=60&ma=no&datalen=100

	{day:"2015-07-02 14:00:00",open:"18.850",high:"18.950",low:"18.500",close:"18.650",volume:"71039840"}
	{day:"2015-07-02 15:00:00",open:"18.660",high:"18.980",low:"18.010",close:"18.650",volume:"129299168"}

数据：开盘价，最高价，最低价，收盘价，交易量（股）

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=240$ma=no&datalen=100

	{day:"2015-07-01",open:"18.330",high:"18.660",low:"18.060",close:"18.210",volume:"293674272"}
	{day:"2015-07-02",open:"18.810",high:"19.180",low:"17.950",close:"18.650",volume:"524774688"}

值得一提的是改成scale=240就变成日K了，scale=1200变成周K，分钟级别的还支持5、15和30分钟 

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=240&datalen=100

	{day:"2015-07-01",open:"18.330",high:"18.660",low:"18.060",close:"18.210",volume:"293674272",ma_price5:18.04,ma_volume5:395533120,ma_price10:18.422,ma_volume10:325295078,ma_price30:19.072,ma_volume30:315460913}
	{day:"2015-07-02",open:"18.810",high:"19.180",low:"17.950",close:"18.650",volume:"524774688",ma_price5:18.082,ma_volume5:435026694,ma_price10:18.344,ma_volume10:352498610,ma_price30:19.092,ma_volume30:321150727}

然后去掉ma=no参数还可以获得5、10和30日均值，简直良心

关于复权数据，以龙力生物2015年6月5日复权为例，当日该股下跌2.26%

http://finance.sina.com.cn/realstock/company/sz002604/qianfuquan.js?d=2015-07-02

	_2015_06_05:"2.076895"
	_2015_06_04:"2.124909"
	2.076895 / 2.124909 = 0.9774

前复权接口

http://finance.sina.com.cn/realstock/company/sz002604/houfuquan.js?d=2015-07-02

	_2015_06_05:"52.5870"
	_2015_06_04:"53.8027"
	52.5870 / 53.8027 = 0.9774

后复权接口

可以看到前后复权接口实际上是一样的，后一日除以前一日得到的值固定

#和讯网历史数据API

http://webstock.quote.hermes.hexun.com/a/kline?code=SSE603019&start=20150702170007&number=-1000&type=5

    [20150604000000,14663,14511,13562,14520,13197,4932830,671311965]
    [20150605000000,13562,13900,13095,14100,12740,5696791,760090971]

数据：前收盘价，开盘价，收盘价，最高价，最低价，成交量，成交额

http://webstock.quote.hermes.hexun.com/a/kline?code=SZSE002604&start=20150702165050&number=-1000&type=5

    [20150604000000,3160,3180,3151,3273,2895,14886410,460637236]
    [20150605000000,1968,2019,1923,2059,1901,27441049,542157326]

可以看到因为有前收盘价做参考，可以做前后复权的计算

另外修改type可以更改K线类型，例如type=4是60分钟K线，type=3是30分钟K线，继续向下是15分钟、5分钟和1分钟，向上只支持到type=6周线
