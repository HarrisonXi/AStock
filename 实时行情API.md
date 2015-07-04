#新浪财经实时行情API

http://hq.sinajs.cn/list=sh000001

    var hq_str_sh000001="上证指数,4058.624,4053.700,3912.767,4080.387,3795.253,0,0,586015612,736006857593,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2015-07-02,15:04:01,00";

http://hq.sinajs.cn/list=sh600036

    var hq_str_sh600036="招商银行,18.81,18.21,18.65,19.18,17.95,18.58,18.60,524774699,9814648360,25500,18.58,36300,18.57,21600,18.56,8100,18.55,32400,18.54,117478,18.60,3000,18.64,469900,18.65,320376,18.66,115700,18.67,2015-07-02,15:04:01,00";

http://hq.sinajs.cn/list=sz000001

    var hq_str_sz000001="平安银行,13.90,13.92,13.75,14.31,13.38,13.75,13.76,198282626,2762337227.52,1091788,13.75,15200,13.74,69300,13.73,16701,13.72,28800,13.71,51900,13.76,334592,13.77,77800,13.78,284700,13.79,62800,13.80,2015-07-02,15:05:12,00";

前6个数据：股名，开盘价，昨收价，现价，最高价，最低价，买一价，卖一价，成交量（股），成交额（元）。后面还有5档买卖数据

支持多个查询逗号隔开，例如：http://hq.sinajs.cn/list=sh603019,sz002024

#新浪财经分时图API

http://vip.stock.finance.sina.com.cn/quotes_service/view/vML_DataList.php?asc=j&symbol=sh600036&num=10

    ['14:59:00', '18.59', '3778240']

数据：价格，成交量（股）

#新浪财经交易明细API

http://vip.stock.finance.sina.com.cn/quotes_service/view/CN_TransListV2.php?num=10&symbol=sh600036

    trade_item_list[2] = new Array('14:59:55', '85920', '18.590', 'DOWN');

数据：成交量(股)，价格，类型（UP-买，DOWN-卖，EQUAL-平）

    trade_INVOL_OUTVOL=[287021989,237752699];

尾部额外带了当日总买入股数和卖出股数

http://vip.stock.finance.sina.com.cn/quotes_service/view/CN_BillList.php?sort=ticktime&symbol=sh600036&num=10

    bill_detail_list[1] = new Array('14:59:55', '85920', '18.590', 'DOWN');

和上面接口返回数据基本一致，没有末尾的买入卖出股数，看上去有点延迟。

#新浪财经资金进出API

http://vip.stock.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20moneyFlowData=/MoneyFlow.ssi_ssfx_flzjtj?daima=sh600036&gettime=1

    var moneyFlowData=(({r0_in:"4755090136.2400",r0_out:"3774078805.3800",r0:"9423742090.1200",r1_in:"146575463.6400",r1_out:"189668586.3200",r1:"376063787.1600",r2_in:"6007462.4000",r2_out:"6635436.4800",r2:"13748567.6800",r3_in:"83154.2400",r3_out:"162677.4400",r3:"270488.9600",curr_capital:"2062894",name:"ÕÐÉÌÒøÐÐ",trade:"18.6500",changeratio:"0.0241625",volume:"524774688.0000",turnover:"254.388",r0x_ratio:"76.4102",opendate:"2015-07-02",ticktime:"15:00:05",netamount:"937210710.9000"}))

数据：r0为特大单成交额（元），之后r1r2r3为大中小单，curr_capital-流通股（万股），trade-现价，changeratio-涨幅，volume-成交量（股），turnover-换手率（x100），netamount-净流入（元）。r0x_ratio表示主力罗盘度，不知道是什么

#和讯网实时行情API

http://webstock.quote.hermes.hexun.com/a/quotelist?code=szse000001&column=DateTime,LastClose,Open,High,Low,Price,Volume,Amount,LastSettle,SettlePrice,OpenPosition,ClosePosition,BuyPrice,BuyVolume,SellPrice,SellVolume,PriceWeight

    ({"Data":[[[20150701150237,1454,1435,1459,1374,1392,183540616,2629096356,0,0,0,0,[1391,1390,1389,1388,1387],[201000,2102782,74800,171300,97400],[1392,1393,1394,1395,1396],[1225986,189942,224200,156715,91100],100]]]});

按照请求参数对应就可以知道对应的数据：昨收，开盘，最高，最低，现价，成交量，成交额。其余数据除了5档买卖都是固定值的样子

去除某些无用的数据，请求可以简化：

http://webstock.quote.hermes.hexun.com/a/quotelist?code=sse600036&column=DateTime,LastClose,Open,High,Low,Price,Volume,Amount

    ({"Data":[[[20150701145959,1872,1833,1866,1806,1821,293674262,5395012371]]]});

#和讯网分时图API

http://webstock.quote.hermes.hexun.com/a/minute?code=sse600036&start=20150701000000&number=6000

因为number为负表示向前取数据，所以可以更改请求为：

http://webstock.quote.hermes.hexun.com/a/minute?code=sse600036&start=20150702000000&number=-100

    [20150701145901,1821,48367788,2656019,0,0]

数据：价格，成交额，成交量，领先指标，大盘红绿柱。后两个数据貌似暂时没值

    1872,1866,1806,100,20150701093000,20150701150000

数组外尾部数据：前收盘价，最高价，最低价，价格倍数。价格倍数貌似固定是100

#和讯网交易明细API

http://webstock.quote.hermes.hexun.com/a/deal?code=sse600036&start=20150701151000&number=-10

    [20150701150001,1820,12417841,682299,1,0,0,0,0,0]

数据：价格，成交额，成交量，交易类型（平盘-0,内盘-1,外盘-2）。后面的数据貌似都没值

    20150701092506,20150701150011,10,1872,100

尾部数据第4个是昨日收盘价

#和讯网成交金额分析API：

http://vol.stock.hexun.com/Charts/Now/Share/info1_stock.ashx?code=600036

XML格式请自行分析

#和讯网大小单统计API

http://vol.stock.hexun.com/Charts/Now/Share/info2_stock.ashx?code=600036

XML格式请自行分析，数据和下面的资金进出接口略有出入

#和讯网60日机构增减仓API：

http://vol.stock.hexun.com/Charts/Now/Share/info3_stock.ashx?code=600036

XML格式请自行分析

#和讯网资金进出API

http://vol.stock.hexun.com/charts/now/share/info4_stock.ashx?code=002604

    [['龙力生物(002604)今日资金进出分析','2015-07-01 15:00'],['13.39','23914.66','-6777.08','178649','4.64'],['13.44','14587.14','507.07','108496','2.82']]

两个数组数据表示大户和散户，数据从前往后为：今日成本（元），资金总额（万元），资金进入（万元），总手，换手率（%）
