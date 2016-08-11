# -*- coding: utf-8 -*-
import sys
import os
import urllib2
import socket
import re
import time
import threading
from aclass import *

threadLock = threading.Lock()
dateTimePattern = re.compile(r',\d{2}(\d{2}-\d{2}-\d{2}),(\d{2}:\d{2}):\d{2},')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^"]+";')
volumePattern = re.compile(r'var hq_str_s[hz]\d{6}="(([^,"]+),){8}([^,"]+),[^"]+";')
transPattern = re.compile(r'new Array\(\'([\d:]+)\', \'(\d+)\', \'([\d\.]+)\', \'(DOWN|UP|EQUAL)\'\)')
klinePattern = re.compile(r'\{day:"([\d\- :]+)",open:"([\d.]+)",high:"([\d.]+)",low:"([\d.]+)",close:"([\d.]+)",volume:"(\d+)"\}')
cahceMode = False # 缓存模式
testMode = False # 测试模式
cachePath = None # 缓存文件夹的路径
timePercent = 0 # 今天交易时间经过的百分比（例:午休-50%，14:00-75%）
correctDate = 0 # 如果没有停牌复牌K线数据第一天的正确日期
totalCount = 0

def calcTimePercent(dateTime):
	timePercent = dateTime % 10000
	if timePercent >= 1500:
		timePercent = 240
	elif timePercent >= 1400:
		timePercent = timePercent - 1400 + 180
	elif timePercent >= 1300:
		timePercent = timePercent - 1300 + 120
	elif timePercent >= 1130:
		timePercent = 120
	elif timePercent >= 1100:
		timePercent = timePercent - 1100 + 90
	elif timePercent >= 1000:
		timePercent = timePercent - 1000 + 30
	elif timePercent >= 930:
		timePercent = timePercent - 930
	else:
		timePercent = 0
	return timePercent / 240.0

def calcDuration(minutes):
	return minutes % 60 + 100 * (minutes / 60)

def requestDateTime_():
	url = 'http://hq.sinajs.cn/list=sh000001'
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	match = dateTimePattern.search(content)
	dateTime = int(match.group(1).replace('-', '')) * 10000 + int(match.group(2).replace(':', ''))
	return dateTime

def requestDateTime():
	dateTime = requestDateTime_()
	while dateTime == False:
		dateTime = requestDateTime_()
	return dateTime

def requestStockData_(stockCode):
	url = 'http://hq.sinajs.cn/list=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	stock = None
	match = stockPattern.search(content)
	if match:
		stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))
	return stock

def requestStockData(stockCode):
	stock = requestStockData_(stockCode)
	while stock == False:
		stock = requestStockData_(stockCode)
	return stock

def requestVolumnData_(stockCode):
	url = 'http://hq.sinajs.cn/list=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	volume = 0
	match = volumePattern.search(content)
	if match:
		volume = int(match.group(3))
	return volume

def requestVolumnData(stockCode):
	volume = requestVolumnData_(stockCode)
	while volume == False:
		volume = requestVolumnData_(stockCode)
	return volume

def requestKlineData_(stockCode, count, scale):
	url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=%s&scale=%d&ma=no&datalen=%d' % (stockCode, scale, count)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	klineList = []
	match = klinePattern.search(content)
	while match:
		kline = Kline(match.group(2), match.group(3), match.group(4), match.group(5), match.group(6), match.group(1))
		klineList.append(kline)
		match = klinePattern.search(content, match.end() + 1)
	return klineList

def requestKlineData(stockCode, count, scale = 240):
	klineList = requestKlineData_(stockCode, count, scale)
	while klineList == False:
		klineList = requestKlineData_(stockCode, count, scale)
	return klineList

def requestCorrectDate():
	klineList = requestKlineData('sh000001', 6)
	if klineList[-1].date == dateTime / 10000 % 1000000:
		return klineList[0].date
	else:
		return klineList[1].date

def requestTransData_(stockCode, count):
	# 1小时最大数据量是1150左右，因为交易系统3秒撮合一次，所以理论最大值为1小时1200
	url = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/CN_TransListV2.php?num=%d&symbol=%s' % (count, stockCode)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	transList = []
	match = transPattern.search(content)
	while match:
		trans = Trans(match.group(1), match.group(2), match.group(3), match.group(4))
		if trans.price > 0 and trans.volume > 0:
			transList.insert(0, trans)
		match = transPattern.search(content, match.end() + 1)
	return transList

def requestTransData(stockCode, minutes = 60):
	filePath = None
	transList = None
	# 判断是不是已收盘，收盘会进入缓存判断逻辑
	if cachePath is not None:
		filePath = os.path.join(cachePath, stockCode)
		# 命中缓存，直接从文件读取
		if os.path.isfile(filePath) == True:
			cacheFile = open(filePath, 'r')
			lines = cacheFile.readlines()
			cacheFile.close()
			transList = []
			for line in lines:
				trans = Trans()
				trans.loadLine(line)
				transList.append(trans)
	# 如果没有命中缓存，从网络请求数据
	if transList is None:
		# 已经收盘，拿到的数据顺带存进文件
		if filePath is not None:
			transList = requestTransData_(stockCode, 4800)
			while transList == False:
				transList = requestTransData_(stockCode, 4800)
			lines = []
			for trans in transList:
				lines.append(trans.saveLine())
			cacheFile = open(filePath, 'w')
			cacheFile.writelines(lines)
			cacheFile.close()
		# 直接请求部分数据
		else:
			transList = requestTransData_(stockCode, 1200 * minutes / 60)
			while transList == False:
				transList = requestTransData_(stockCode, 1200 * minutes / 60)
	# 仅筛取指定时间内的数据
	filteredList = []
	if len(transList) > 0:
		validTime = transList[-1].time - calcDuration(minutes)
		for trans in transList:
			if trans.time > validTime:
				filteredList.append(trans)
	return filteredList

def cacheTransData(stockCode):
	# 仅仅尝试缓存数据
	transList = requestTransData(stockCode, 0)

def checkStockData(stockCode):
	# 获得股票名称等数据
	stock = requestStockData(stockCode)
	# 排序无效股票并提示
	if stock == None:
		threadLock.acquire()
		print('==== ' + stockCode[2:] + ' ====')
		print('无效代码')
		threadLock.release()
	# 排除停牌股票
	if stock.todayStart == 0 or stock.yesterdayEnd == 0:
		return
	# 排除跌幅较大的股票
	if testMode == False and stock.current < stock.yesterdayEnd * 0.97:
		return
	# 获取K线数据
	klineList = requestKlineData(stockCode, 6)
	if klineList[-1].date != dateTime / 10000 % 1000000:
		del klineList[0]
	# 有复牌情况则排除
	if klineList[0].date != correctDate:
		return
	# 如果今日数据没有拉取到需要手动计算补全
	if len(klineList) < 6:
		# 获取当前交易量，并计算成今日期望总交易量
		totalVolume = requestVolumnData(stockCode)
		totalVolume = int(totalVolume / timePercent)
		# 合成一个今天的假K线数据方便计算
		kline = Kline(stock.todayStart, stock.highest, stock.lowest, stock.current, totalVolume)
		klineList.append(kline)
	# 有复权情况则排除
	for index in range(0, 5):
		if klineList[index + 1].lowest < klineList[index].end * 0.89:
			return
	# 计算量比
	volume5 = 0
	for kline in klineList[0:5]:
		volume5 += kline.volume
	volumeRatio5 = klineList[-1].volume * 5.0 / volume5
	volumeRatio1 = klineList[-1].volume * 1.0 / klineList[-2].volume
	# 排除量比增长较小的股票
	if testMode == False and (volumeRatio1 < 1.2 or volumeRatio5 < 1.1):
		return
	# 计算日OBV
	obvDay = 0
	for index in xrange(0, 5):
		if klineList[index+1].end > klineList[index].end:
			obvDay += klineList[index+1].volume
		else:
			obvDay -= klineList[index+1].volume
	obvDay = obvDay * 1.0 / volume5
	# 排除OBV低的股票
	if testMode == False and obvDay <= 0:
		return
	# 计算小时OBV
	klineList = requestKlineData(stockCode, 3 * 4 + 1, 60)
	obvHour = 0
	for index in xrange(0, 3 * 4):
		if klineList[index+1].end > klineList[index].end:
			obvHour += klineList[index+1].volume
		else:
			obvHour -= klineList[index+1].volume
	obvHour = obvHour * 2.0 / volume5
	# 排除OBV低的股票
	if testMode == False and obvHour <= 0:
		return
	# 计算15分钟OBV
	klineList = requestKlineData(stockCode, 16 + 1, 15)
	obv15M = 0
	for index in xrange(0, 16):
		if klineList[index+1].end > klineList[index].end:
			obv15M += klineList[index+1].volume
		else:
			obv15M -= klineList[index+1].volume
	obv15M = obv15M * 6.0 / volume5
	# 排除OBV低的股票
	if testMode == False and obv15M <= 0:
		return
	# 打印数据
	threadLock.acquire()
	global totalCount
	totalCount += 1
	print('==== ' + stockCode[2:] + ' ====')
	stock.printStockData()
	print('量    比:  (5)%.2f (1)%.2f' % (volumeRatio5, volumeRatio1))
	print('量价得分:  (日)%.2f (时)%.2f (15分)%.2f' % (obvDay, obvHour, obv15M))
	threadLock.release()

def threadFunction(stockList):
	if cahceMode == True:
		if timePercent == 1.0:
			for stockCode in stockList:
				cacheTransData(stockCode)
	elif testMode == True:
		checkStockData(stockList[0])
	else:
		for stockCode in stockList:
			checkStockData(stockCode)

# 判断是否开启特殊模式
if len(sys.argv) > 1:
	if sys.argv[1] == 'cache':
		cahceMode = True
	elif sys.argv[1] == 'test':
		testMode = True
# 获取当前新浪服务器时间
dateTime = requestDateTime()
timePercent = calcTimePercent(dateTime)
correctDate = requestCorrectDate()
# 如果尚未收盘但是使用的是缓存模式则退出
if timePercent < 1.0 and cahceMode == True:
	print('尚未收盘，无法进行逐比交易明细缓存')
	exit(0)
# 如果已经收盘，则准备好cache目录
if timePercent == 1.0:
	cachePath = os.path.join(sys.path[0], 'cache')
	dateStr = '%6d' % (dateTime / 10000 % 1000000)
	cachePath = os.path.join(cachePath, dateStr)
	if os.path.isdir(cachePath) == False:
		os.mkdir(cachePath)
# 多线循环筛选所有股票数据
startTime = time.time()
validStockList = ['sh600000','sh600004','sh600005','sh600006','sh600007','sh600008','sh600009','sh600010','sh600011','sh600012','sh600015','sh600016','sh600017','sh600018','sh600019','sh600020','sh600021','sh600022','sh600023','sh600026','sh600027','sh600028','sh600029','sh600030','sh600031','sh600033','sh600035','sh600036','sh600037','sh600038','sh600039','sh600048','sh600050','sh600051','sh600052','sh600053','sh600054','sh600055','sh600056','sh600057','sh600058','sh600059','sh600060','sh600061','sh600062','sh600063','sh600064','sh600066','sh600067','sh600068','sh600069','sh600070','sh600071','sh600072','sh600073','sh600074','sh600075','sh600076','sh600077','sh600078','sh600079','sh600080','sh600081','sh600082','sh600083','sh600084','sh600085','sh600086','sh600088','sh600089','sh600090','sh600091','sh600093','sh600094','sh600095','sh600096','sh600097','sh600098','sh600099','sh600100','sh600101','sh600103','sh600104','sh600105','sh600106','sh600107','sh600108','sh600109','sh600110','sh600111','sh600112','sh600113','sh600114','sh600115','sh600116','sh600117','sh600118','sh600119','sh600120','sh600121','sh600122','sh600123','sh600125','sh600126','sh600127','sh600128','sh600129','sh600130','sh600131','sh600132','sh600133','sh600135','sh600136','sh600137','sh600138','sh600139','sh600141','sh600143','sh600145','sh600146','sh600148','sh600149','sh600150','sh600151','sh600152','sh600153','sh600155','sh600156','sh600157','sh600158','sh600159','sh600160','sh600161','sh600162','sh600163','sh600165','sh600166','sh600167','sh600168','sh600169','sh600170','sh600171','sh600172','sh600173','sh600175','sh600176','sh600177','sh600178','sh600179','sh600180','sh600182','sh600183','sh600184','sh600185','sh600186','sh600187','sh600188','sh600189','sh600190','sh600191','sh600192','sh600193','sh600195','sh600196','sh600197','sh600198','sh600199','sh600200','sh600201','sh600202','sh600203','sh600206','sh600207','sh600208','sh600209','sh600210','sh600211','sh600212','sh600213','sh600215','sh600216','sh600217','sh600218','sh600219','sh600220','sh600221','sh600222','sh600223','sh600225','sh600226','sh600227','sh600228','sh600229','sh600230','sh600231','sh600232','sh600233','sh600234','sh600235','sh600236','sh600237','sh600238','sh600239','sh600240','sh600241','sh600242','sh600243','sh600246','sh600247','sh600248','sh600249','sh600250','sh600251','sh600252','sh600255','sh600256','sh600257','sh600258','sh600259','sh600260','sh600261','sh600262','sh600265','sh600266','sh600267','sh600268','sh600269','sh600270','sh600271','sh600272','sh600273','sh600275','sh600276','sh600277','sh600278','sh600279','sh600280','sh600281','sh600282','sh600283','sh600284','sh600285','sh600287','sh600288','sh600289','sh600290','sh600291','sh600292','sh600293','sh600295','sh600297','sh600298','sh600299','sh600300','sh600301','sh600302','sh600303','sh600305','sh600306','sh600307','sh600308','sh600309','sh600310','sh600311','sh600312','sh600313','sh600315','sh600316','sh600317','sh600318','sh600319','sh600320','sh600321','sh600322','sh600323','sh600325','sh600326','sh600327','sh600328','sh600329','sh600330','sh600331','sh600332','sh600333','sh600335','sh600336','sh600337','sh600338','sh600339','sh600340','sh600343','sh600345','sh600346','sh600348','sh600350','sh600351','sh600352','sh600353','sh600354','sh600355','sh600356','sh600358','sh600359','sh600360','sh600361','sh600362','sh600363','sh600365','sh600366','sh600367','sh600368','sh600369','sh600370','sh600371','sh600372','sh600373','sh600375','sh600376','sh600377','sh600378','sh600379','sh600380','sh600381','sh600382','sh600383','sh600385','sh600386','sh600387','sh600388','sh600389','sh600390','sh600391','sh600392','sh600393','sh600395','sh600396','sh600397','sh600398','sh600399','sh600400','sh600401','sh600403','sh600405','sh600406','sh600408','sh600409','sh600410','sh600415','sh600416','sh600418','sh600419','sh600420','sh600421','sh600422','sh600423','sh600425','sh600426','sh600428','sh600429','sh600432','sh600433','sh600435','sh600436','sh600438','sh600439','sh600444','sh600446','sh600448','sh600449','sh600452','sh600455','sh600456','sh600458','sh600459','sh600460','sh600461','sh600462','sh600463','sh600466','sh600467','sh600468','sh600469','sh600470','sh600475','sh600476','sh600477','sh600478','sh600479','sh600480','sh600481','sh600482','sh600483','sh600485','sh600486','sh600487','sh600488','sh600489','sh600490','sh600491','sh600493','sh600495','sh600496','sh600497','sh600498','sh600499','sh600500','sh600501','sh600502','sh600503','sh600505','sh600506','sh600507','sh600508','sh600509','sh600510','sh600511','sh600512','sh600513','sh600515','sh600516','sh600517','sh600518','sh600519','sh600520','sh600521','sh600522','sh600523','sh600525','sh600526','sh600527','sh600528','sh600529','sh600530','sh600531','sh600532','sh600533','sh600535','sh600536','sh600537','sh600538','sh600539','sh600540','sh600543','sh600545','sh600546','sh600547','sh600548','sh600549','sh600550','sh600551','sh600552','sh600555','sh600556','sh600557','sh600558','sh600559','sh600560','sh600561','sh600562','sh600563','sh600565','sh600566','sh600567','sh600568','sh600569','sh600570','sh600571','sh600572','sh600573','sh600575','sh600576','sh600577','sh600578','sh600579','sh600580','sh600581','sh600582','sh600583','sh600584','sh600585','sh600586','sh600587','sh600588','sh600589','sh600590','sh600592','sh600593','sh600594','sh600595','sh600596','sh600597','sh600598','sh600599','sh600600','sh600601','sh600602','sh600603','sh600604','sh600605','sh600606','sh600608','sh600609','sh600610','sh600611','sh600612','sh600613','sh600614','sh600615','sh600616','sh600617','sh600618','sh600619','sh600620','sh600621','sh600622','sh600623','sh600624','sh600626','sh600628','sh600629','sh600630','sh600633','sh600634','sh600635','sh600636','sh600637','sh600638','sh600639','sh600640','sh600641','sh600642','sh600643','sh600644','sh600645','sh600647','sh600648','sh600649','sh600650','sh600651','sh600652','sh600653','sh600654','sh600655','sh600656','sh600657','sh600658','sh600660','sh600661','sh600662','sh600663','sh600664','sh600665','sh600666','sh600667','sh600668','sh600671','sh600673','sh600674','sh600675','sh600676','sh600677','sh600678','sh600679','sh600680','sh600681','sh600682','sh600683','sh600684','sh600685','sh600686','sh600687','sh600688','sh600689','sh600690','sh600691','sh600692','sh600693','sh600694','sh600695','sh600696','sh600697','sh600698','sh600699','sh600701','sh600702','sh600703','sh600704','sh600705','sh600706','sh600707','sh600708','sh600710','sh600711','sh600712','sh600713','sh600714','sh600715','sh600716','sh600717','sh600718','sh600719','sh600720','sh600721','sh600722','sh600723','sh600724','sh600725','sh600726','sh600727','sh600728','sh600729','sh600730','sh600731','sh600732','sh600733','sh600734','sh600735','sh600736','sh600737','sh600738','sh600739','sh600740','sh600741','sh600742','sh600743','sh600744','sh600745','sh600746','sh600747','sh600748','sh600749','sh600750','sh600751','sh600753','sh600754','sh600755','sh600756','sh600757','sh600758','sh600759','sh600760','sh600761','sh600763','sh600764','sh600765','sh600766','sh600767','sh600768','sh600769','sh600770','sh600771','sh600773','sh600774','sh600775','sh600776','sh600777','sh600778','sh600779','sh600780','sh600781','sh600782','sh600783','sh600784','sh600785','sh600787','sh600789','sh600790','sh600791','sh600792','sh600793','sh600794','sh600795','sh600796','sh600797','sh600798','sh600800','sh600801','sh600802','sh600803','sh600804','sh600805','sh600806','sh600807','sh600808','sh600809','sh600810','sh600811','sh600812','sh600814','sh600815','sh600816','sh600817','sh600818','sh600819','sh600820','sh600821','sh600822','sh600823','sh600824','sh600825','sh600826','sh600827','sh600828','sh600829','sh600830','sh600831','sh600833','sh600834','sh600835','sh600836','sh600837','sh600838','sh600839','sh600841','sh600843','sh600844','sh600845','sh600846','sh600847','sh600848','sh600850','sh600851','sh600853','sh600854','sh600855','sh600856','sh600857','sh600858','sh600859','sh600860','sh600861','sh600862','sh600863','sh600864','sh600865','sh600866','sh600867','sh600868','sh600869','sh600870','sh600871','sh600872','sh600873','sh600874','sh600875','sh600876','sh600877','sh600879','sh600880','sh600881','sh600882','sh600883','sh600884','sh600885','sh600886','sh600887','sh600888','sh600889','sh600890','sh600891','sh600892','sh600893','sh600894','sh600895','sh600896','sh600897','sh600898','sh600900','sh600917','sh600958','sh600959','sh600960','sh600961','sh600962','sh600963','sh600965','sh600966','sh600967','sh600969','sh600970','sh600971','sh600973','sh600975','sh600976','sh600978','sh600979','sh600980','sh600981','sh600982','sh600983','sh600984','sh600985','sh600986','sh600987','sh600988','sh600990','sh600992','sh600993','sh600995','sh600997','sh600998','sh600999','sh601000','sh601001','sh601002','sh601003','sh601005','sh601006','sh601007','sh601008','sh601009','sh601010','sh601011','sh601012','sh601015','sh601016','sh601018','sh601020','sh601021','sh601028','sh601038','sh601058','sh601069','sh601088','sh601098','sh601099','sh601100','sh601101','sh601106','sh601107','sh601111','sh601113','sh601116','sh601117','sh601118','sh601126','sh601127','sh601137','sh601139','sh601155','sh601158','sh601166','sh601168','sh601169','sh601177','sh601179','sh601186','sh601188','sh601198','sh601199','sh601208','sh601211','sh601216','sh601218','sh601222','sh601225','sh601226','sh601231','sh601233','sh601238','sh601258','sh601288','sh601311','sh601313','sh601318','sh601328','sh601333','sh601336','sh601339','sh601368','sh601369','sh601377','sh601388','sh601390','sh601398','sh601515','sh601518','sh601519','sh601555','sh601558','sh601566','sh601567','sh601579','sh601588','sh601599','sh601600','sh601601','sh601607','sh601608','sh601611','sh601616','sh601618','sh601628','sh601633','sh601636','sh601666','sh601668','sh601669','sh601677','sh601678','sh601688','sh601689','sh601699','sh601700','sh601717','sh601718','sh601727','sh601766','sh601777','sh601788','sh601789','sh601798','sh601799','sh601800','sh601801','sh601808','sh601818','sh601857','sh601866','sh601872','sh601877','sh601880','sh601886','sh601888','sh601890','sh601898','sh601899','sh601900','sh601901','sh601908','sh601918','sh601919','sh601928','sh601929','sh601933','sh601939','sh601958','sh601965','sh601968','sh601969','sh601985','sh601988','sh601989','sh601991','sh601992','sh601996','sh601998','sh601999','sh603000','sh603001','sh603002','sh603003','sh603005','sh603006','sh603008','sh603009','sh603010','sh603011','sh603012','sh603015','sh603017','sh603018','sh603019','sh603020','sh603021','sh603022','sh603023','sh603025','sh603026','sh603027','sh603028','sh603029','sh603030','sh603066','sh603077','sh603085','sh603088','sh603099','sh603100','sh603101','sh603108','sh603111','sh603116','sh603117','sh603118','sh603123','sh603126','sh603128','sh603131','sh603158','sh603166','sh603167','sh603168','sh603169','sh603188','sh603198','sh603199','sh603222','sh603223','sh603227','sh603268','sh603288','sh603299','sh603300','sh603306','sh603308','sh603309','sh603311','sh603315','sh603318','sh603328','sh603333','sh603338','sh603339','sh603355','sh603366','sh603368','sh603369','sh603377','sh603398','sh603399','sh603456','sh603508','sh603518','sh603519','sh603520','sh603528','sh603555','sh603558','sh603566','sh603567','sh603568','sh603588','sh603589','sh603598','sh603599','sh603600','sh603601','sh603606','sh603608','sh603609','sh603611','sh603616','sh603618','sh603636','sh603669','sh603678','sh603686','sh603688','sh603696','sh603698','sh603699','sh603701','sh603703','sh603718','sh603726','sh603729','sh603737','sh603766','sh603778','sh603779','sh603788','sh603789','sh603798','sh603799','sh603800','sh603806','sh603808','sh603818','sh603822','sh603828','sh603838','sh603861','sh603866','sh603868','sh603869','sh603883','sh603885','sh603889','sh603898','sh603899','sh603901','sh603909','sh603918','sh603919','sh603936','sh603939','sh603958','sh603959','sh603968','sh603969','sh603979','sh603988','sh603989','sh603993','sh603996','sh603997','sh603998','sh603999','sz000001','sz000002','sz000004','sz000005','sz000006','sz000007','sz000008','sz000009','sz000010','sz000011','sz000012','sz000014','sz000016','sz000017','sz000018','sz000019','sz000020','sz000021','sz000022','sz000023','sz000025','sz000026','sz000027','sz000028','sz000029','sz000030','sz000031','sz000032','sz000034','sz000035','sz000036','sz000037','sz000038','sz000039','sz000040','sz000042','sz000043','sz000045','sz000046','sz000048','sz000049','sz000050','sz000055','sz000056','sz000058','sz000059','sz000060','sz000061','sz000062','sz000063','sz000065','sz000066','sz000068','sz000069','sz000070','sz000078','sz000088','sz000089','sz000090','sz000096','sz000099','sz000100','sz000150','sz000151','sz000153','sz000155','sz000156','sz000157','sz000158','sz000159','sz000166','sz000301','sz000333','sz000338','sz000400','sz000401','sz000402','sz000403','sz000404','sz000407','sz000408','sz000409','sz000410','sz000411','sz000413','sz000415','sz000416','sz000417','sz000418','sz000419','sz000420','sz000421','sz000422','sz000423','sz000425','sz000426','sz000428','sz000429','sz000430','sz000488','sz000498','sz000501','sz000502','sz000503','sz000504','sz000505','sz000506','sz000507','sz000509','sz000510','sz000511','sz000513','sz000514','sz000516','sz000517','sz000518','sz000519','sz000520','sz000521','sz000523','sz000524','sz000525','sz000526','sz000528','sz000529','sz000530','sz000531','sz000532','sz000533','sz000534','sz000536','sz000537','sz000538','sz000539','sz000540','sz000541','sz000543','sz000544','sz000545','sz000546','sz000547','sz000548','sz000550','sz000551','sz000552','sz000553','sz000554','sz000555','sz000557','sz000558','sz000559','sz000560','sz000561','sz000563','sz000564','sz000565','sz000566','sz000567','sz000568','sz000570','sz000571','sz000572','sz000573','sz000576','sz000581','sz000582','sz000584','sz000585','sz000586','sz000587','sz000589','sz000590','sz000591','sz000592','sz000593','sz000595','sz000596','sz000597','sz000598','sz000599','sz000600','sz000601','sz000603','sz000605','sz000606','sz000607','sz000608','sz000609','sz000610','sz000611','sz000612','sz000613','sz000615','sz000616','sz000617','sz000619','sz000620','sz000622','sz000623','sz000625','sz000626','sz000627','sz000628','sz000629','sz000630','sz000631','sz000632','sz000633','sz000635','sz000636','sz000637','sz000638','sz000639','sz000650','sz000651','sz000652','sz000655','sz000656','sz000657','sz000659','sz000661','sz000662','sz000663','sz000665','sz000666','sz000667','sz000668','sz000669','sz000670','sz000671','sz000672','sz000673','sz000676','sz000677','sz000678','sz000679','sz000680','sz000681','sz000682','sz000683','sz000685','sz000686','sz000687','sz000688','sz000690','sz000691','sz000692','sz000693','sz000695','sz000697','sz000698','sz000700','sz000701','sz000702','sz000703','sz000705','sz000707','sz000708','sz000709','sz000710','sz000711','sz000712','sz000713','sz000715','sz000716','sz000717','sz000718','sz000719','sz000720','sz000721','sz000722','sz000723','sz000725','sz000726','sz000727','sz000728','sz000729','sz000731','sz000732','sz000733','sz000735','sz000736','sz000737','sz000738','sz000739','sz000748','sz000750','sz000751','sz000752','sz000753','sz000755','sz000756','sz000757','sz000758','sz000759','sz000760','sz000761','sz000762','sz000766','sz000767','sz000768','sz000776','sz000777','sz000778','sz000779','sz000780','sz000782','sz000783','sz000785','sz000786','sz000788','sz000789','sz000790','sz000791','sz000792','sz000793','sz000795','sz000796','sz000797','sz000798','sz000799','sz000800','sz000801','sz000802','sz000803','sz000806','sz000807','sz000809','sz000810','sz000811','sz000812','sz000813','sz000815','sz000816','sz000818','sz000819','sz000820','sz000821','sz000822','sz000823','sz000825','sz000826','sz000828','sz000829','sz000830','sz000831','sz000833','sz000835','sz000836','sz000837','sz000838','sz000839','sz000848','sz000850','sz000851','sz000852','sz000856','sz000858','sz000859','sz000860','sz000861','sz000862','sz000863','sz000868','sz000869','sz000875','sz000876','sz000877','sz000878','sz000880','sz000881','sz000882','sz000883','sz000885','sz000886','sz000887','sz000888','sz000889','sz000890','sz000892','sz000893','sz000895','sz000897','sz000898','sz000899','sz000900','sz000901','sz000902','sz000903','sz000905','sz000906','sz000908','sz000909','sz000910','sz000911','sz000912','sz000913','sz000915','sz000916','sz000917','sz000918','sz000919','sz000920','sz000921','sz000922','sz000923','sz000925','sz000926','sz000927','sz000928','sz000929','sz000930','sz000931','sz000932','sz000933','sz000935','sz000936','sz000937','sz000938','sz000939','sz000948','sz000949','sz000950','sz000951','sz000952','sz000953','sz000955','sz000957','sz000958','sz000959','sz000960','sz000961','sz000962','sz000963','sz000965','sz000966','sz000967','sz000968','sz000969','sz000970','sz000971','sz000972','sz000973','sz000975','sz000976','sz000977','sz000978','sz000979','sz000980','sz000981','sz000982','sz000983','sz000985','sz000987','sz000988','sz000989','sz000990','sz000993','sz000995','sz000996','sz000997','sz000998','sz000999','sz001696','sz001896','sz001979','sz002001','sz002002','sz002003','sz002004','sz002005','sz002006','sz002007','sz002008','sz002009','sz002010','sz002011','sz002012','sz002013','sz002014','sz002015','sz002016','sz002017','sz002018','sz002019','sz002020','sz002021','sz002022','sz002023','sz002024','sz002025','sz002026','sz002027','sz002028','sz002029','sz002030','sz002031','sz002032','sz002033','sz002034','sz002035','sz002036','sz002037','sz002038','sz002039','sz002040','sz002041','sz002042','sz002043','sz002044','sz002045','sz002046','sz002047','sz002048','sz002049','sz002050','sz002051','sz002052','sz002053','sz002054','sz002055','sz002056','sz002057','sz002058','sz002059','sz002060','sz002061','sz002062','sz002063','sz002064','sz002065','sz002066','sz002067','sz002068','sz002069','sz002070','sz002071','sz002072','sz002073','sz002074','sz002075','sz002076','sz002077','sz002078','sz002079','sz002080','sz002081','sz002082','sz002083','sz002084','sz002085','sz002086','sz002087','sz002088','sz002089','sz002090','sz002091','sz002092','sz002093','sz002094','sz002095','sz002096','sz002097','sz002098','sz002099','sz002100','sz002101','sz002102','sz002103','sz002104','sz002105','sz002106','sz002107','sz002108','sz002109','sz002110','sz002111','sz002112','sz002113','sz002114','sz002115','sz002116','sz002117','sz002118','sz002119','sz002120','sz002121','sz002122','sz002123','sz002124','sz002125','sz002126','sz002127','sz002128','sz002129','sz002130','sz002131','sz002132','sz002133','sz002134','sz002135','sz002136','sz002137','sz002138','sz002139','sz002140','sz002141','sz002142','sz002143','sz002144','sz002145','sz002146','sz002147','sz002148','sz002149','sz002150','sz002151','sz002152','sz002153','sz002154','sz002155','sz002156','sz002157','sz002158','sz002159','sz002160','sz002161','sz002162','sz002163','sz002164','sz002165','sz002166','sz002167','sz002168','sz002169','sz002170','sz002171','sz002172','sz002173','sz002174','sz002175','sz002176','sz002177','sz002178','sz002179','sz002180','sz002181','sz002182','sz002183','sz002184','sz002185','sz002186','sz002187','sz002188','sz002189','sz002190','sz002191','sz002192','sz002193','sz002194','sz002195','sz002196','sz002197','sz002198','sz002199','sz002200','sz002201','sz002202','sz002203','sz002204','sz002205','sz002206','sz002207','sz002208','sz002209','sz002210','sz002211','sz002212','sz002213','sz002214','sz002215','sz002216','sz002217','sz002218','sz002219','sz002220','sz002221','sz002222','sz002223','sz002224','sz002225','sz002226','sz002227','sz002228','sz002229','sz002230','sz002231','sz002232','sz002233','sz002234','sz002235','sz002236','sz002237','sz002238','sz002239','sz002240','sz002241','sz002242','sz002243','sz002244','sz002245','sz002246','sz002247','sz002248','sz002249','sz002250','sz002251','sz002252','sz002253','sz002254','sz002255','sz002256','sz002258','sz002259','sz002260','sz002261','sz002262','sz002263','sz002264','sz002265','sz002266','sz002267','sz002268','sz002269','sz002270','sz002271','sz002272','sz002273','sz002274','sz002275','sz002276','sz002277','sz002278','sz002279','sz002280','sz002281','sz002282','sz002283','sz002284','sz002285','sz002286','sz002287','sz002288','sz002289','sz002290','sz002291','sz002292','sz002293','sz002294','sz002295','sz002296','sz002297','sz002298','sz002299','sz002300','sz002301','sz002302','sz002303','sz002304','sz002305','sz002306','sz002307','sz002308','sz002309','sz002310','sz002311','sz002312','sz002313','sz002314','sz002315','sz002316','sz002317','sz002318','sz002319','sz002320','sz002321','sz002322','sz002323','sz002324','sz002325','sz002326','sz002327','sz002328','sz002329','sz002330','sz002331','sz002332','sz002333','sz002334','sz002335','sz002336','sz002337','sz002338','sz002339','sz002340','sz002341','sz002342','sz002343','sz002344','sz002345','sz002346','sz002347','sz002348','sz002349','sz002350','sz002351','sz002352','sz002353','sz002354','sz002355','sz002356','sz002357','sz002358','sz002359','sz002360','sz002361','sz002362','sz002363','sz002364','sz002365','sz002366','sz002367','sz002368','sz002369','sz002370','sz002371','sz002372','sz002373','sz002374','sz002375','sz002376','sz002377','sz002378','sz002379','sz002380','sz002381','sz002382','sz002383','sz002384','sz002385','sz002386','sz002387','sz002388','sz002389','sz002390','sz002391','sz002392','sz002393','sz002394','sz002395','sz002396','sz002397','sz002398','sz002399','sz002400','sz002401','sz002402','sz002403','sz002404','sz002405','sz002406','sz002407','sz002408','sz002409','sz002410','sz002411','sz002412','sz002413','sz002414','sz002415','sz002416','sz002417','sz002418','sz002419','sz002420','sz002421','sz002422','sz002423','sz002424','sz002425','sz002426','sz002427','sz002428','sz002429','sz002430','sz002431','sz002432','sz002433','sz002434','sz002435','sz002436','sz002437','sz002438','sz002439','sz002440','sz002441','sz002442','sz002443','sz002444','sz002445','sz002446','sz002447','sz002448','sz002449','sz002450','sz002451','sz002452','sz002453','sz002454','sz002455','sz002456','sz002457','sz002458','sz002459','sz002460','sz002461','sz002462','sz002463','sz002464','sz002465','sz002466','sz002467','sz002468','sz002469','sz002470','sz002471','sz002472','sz002473','sz002474','sz002475','sz002476','sz002477','sz002478','sz002479','sz002480','sz002481','sz002482','sz002483','sz002484','sz002485','sz002486','sz002487','sz002488','sz002489','sz002490','sz002491','sz002492','sz002493','sz002494','sz002495','sz002496','sz002497','sz002498','sz002499','sz002500','sz002501','sz002502','sz002503','sz002504','sz002505','sz002506','sz002507','sz002508','sz002509','sz002510','sz002511','sz002512','sz002513','sz002514','sz002515','sz002516','sz002517','sz002518','sz002519','sz002520','sz002521','sz002522','sz002523','sz002524','sz002526','sz002527','sz002528','sz002529','sz002530','sz002531','sz002532','sz002533','sz002534','sz002535','sz002536','sz002537','sz002538','sz002539','sz002540','sz002541','sz002542','sz002543','sz002544','sz002545','sz002546','sz002547','sz002548','sz002549','sz002550','sz002551','sz002552','sz002553','sz002554','sz002555','sz002556','sz002557','sz002558','sz002559','sz002560','sz002561','sz002562','sz002563','sz002564','sz002565','sz002566','sz002567','sz002568','sz002569','sz002570','sz002571','sz002572','sz002573','sz002574','sz002575','sz002576','sz002577','sz002578','sz002579','sz002580','sz002581','sz002582','sz002583','sz002584','sz002585','sz002586','sz002587','sz002588','sz002589','sz002590','sz002591','sz002592','sz002593','sz002594','sz002595','sz002596','sz002597','sz002598','sz002599','sz002600','sz002601','sz002602','sz002603','sz002604','sz002605','sz002606','sz002607','sz002608','sz002609','sz002610','sz002611','sz002612','sz002613','sz002614','sz002615','sz002616','sz002617','sz002618','sz002619','sz002620','sz002621','sz002622','sz002623','sz002624','sz002625','sz002626','sz002627','sz002628','sz002629','sz002630','sz002631','sz002632','sz002633','sz002634','sz002635','sz002636','sz002637','sz002638','sz002639','sz002640','sz002641','sz002642','sz002643','sz002644','sz002645','sz002646','sz002647','sz002648','sz002649','sz002650','sz002651','sz002652','sz002653','sz002654','sz002655','sz002656','sz002657','sz002658','sz002659','sz002660','sz002661','sz002662','sz002663','sz002664','sz002665','sz002666','sz002667','sz002668','sz002669','sz002670','sz002671','sz002672','sz002673','sz002674','sz002675','sz002676','sz002677','sz002678','sz002679','sz002680','sz002681','sz002682','sz002683','sz002684','sz002685','sz002686','sz002687','sz002688','sz002689','sz002690','sz002691','sz002692','sz002693','sz002694','sz002695','sz002696','sz002697','sz002698','sz002699','sz002700','sz002701','sz002702','sz002703','sz002705','sz002706','sz002707','sz002708','sz002709','sz002711','sz002712','sz002713','sz002714','sz002715','sz002716','sz002717','sz002718','sz002719','sz002721','sz002722','sz002723','sz002724','sz002725','sz002726','sz002727','sz002728','sz002729','sz002730','sz002731','sz002732','sz002733','sz002734','sz002735','sz002736','sz002737','sz002738','sz002739','sz002740','sz002741','sz002742','sz002743','sz002745','sz002746','sz002747','sz002748','sz002749','sz002750','sz002751','sz002752','sz002753','sz002755','sz002756','sz002757','sz002758','sz002759','sz002760','sz002761','sz002762','sz002763','sz002765','sz002766','sz002767','sz002768','sz002769','sz002770','sz002771','sz002772','sz002773','sz002775','sz002776','sz002777','sz002778','sz002779','sz002780','sz002781','sz002782','sz002783','sz002785','sz002786','sz002787','sz002788','sz002789','sz002790','sz002791','sz002792','sz002793','sz002795','sz002796','sz002797','sz002798','sz002799','sz002800','sz002801','sz002802']
countPerThread = (len(validStockList) + 99) / 100 if testMode == False else (len(validStockList) + 9) / 10
threadCount = (len(validStockList) + countPerThread - 1) / countPerThread
threadList = []
for index in xrange(0, threadCount):
	thread = threading.Thread(target = threadFunction, args = (validStockList[index * countPerThread:(index + 1) * countPerThread],))
	threadList.append(thread)
for thread in threadList:
	thread.start()
for thread in threadList:
	thread.join()
print('================')
print('总数量: %d') % (totalCount)
print('总用时: %.2f秒' % (time.time() - startTime))
