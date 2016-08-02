# 新浪财经历史数据API

## K线数据

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=60&ma=no&datalen=100

	{day:"2015-07-02 14:00:00",open:"18.850",high:"18.950",low:"18.500",close:"18.650",volume:"71039840"}
	{day:"2015-07-02 15:00:00",open:"18.660",high:"18.980",low:"18.010",close:"18.650",volume:"129299168"}

数据：日期时间，开盘价，最高价，最低价，收盘价，交易量（股）

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=240&ma=no&datalen=100

	{day:"2015-07-01",open:"18.330",high:"18.660",low:"18.060",close:"18.210",volume:"293674272"}
	{day:"2015-07-02",open:"18.810",high:"19.180",low:"17.950",close:"18.650",volume:"524774688"}

值得一提的是改成scale=240就变成日K了，scale=1200变成周K，分钟级别的还支持5、15和30分钟 

http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600036&scale=240&datalen=100

	{day:"2015-07-01",open:"18.330",high:"18.660",low:"18.060",close:"18.210",volume:"293674272",ma_price5:18.04,ma_volume5:395533120,ma_price10:18.422,ma_volume10:325295078,ma_price30:19.072,ma_volume30:315460913}
	{day:"2015-07-02",open:"18.810",high:"19.180",low:"17.950",close:"18.650",volume:"524774688",ma_price5:18.082,ma_volume5:435026694,ma_price10:18.344,ma_volume10:352498610,ma_price30:19.092,ma_volume30:321150727}

然后去掉ma=no参数还可以获得5、10和30日均价均值

## 复权数据

关于复权数据，以龙力生物2015年6月5日复权为例，当日该股下跌2.26%

http://finance.sina.com.cn/realstock/newcompany/sz002604/phfq.js?_=14

	_2015_06_05:"52.5870",
	_2015_06_04:"53.8027",

52.5870 / 53.8027 = 0.9774，和下跌2.26%一致
