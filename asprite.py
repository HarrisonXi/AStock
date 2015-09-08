# -*- coding: utf-8 -*-
import sys
import urllib2
import socket
import re
import time
import threading
from aclass import *

threadLock = threading.Lock()
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^"]+";')
transPattern = re.compile(r'new Array\(\'([\d:]+)\', \'(\d+)\', \'([\d\.]+)\', \'(DOWN|UP|EQUAL)\'\)')

def requestStockData(stockCode):
	url = 'http://hq.sinajs.cn/list=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	match = stockPattern.search(content)
	stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4))
	return stock

def checkStockTrans(stockCode, forceShow = False):
	# 1小时最大数据量是1150左右，因为交易系统3秒撮合一次，所以理论最大值为1小时1200
	url = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/CN_TransListV2.php?num=1200&symbol=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	# 抓取数据存入数组，仅存入1小时以内的数据
	validTime = 0
	transList = []
	match = transPattern.search(content)
	while match:
		trans = Trans(match.group(1), match.group(2), match.group(3), match.group(4))
		if validTime == 0:
			validTime = trans.time - 100
		if trans.time >= validTime:
			transList.insert(0, trans)
		else:
			break
		match = transPattern.search(content, match.end() + 1)
	# 检查数据，确定有数据的情况下进入筛选逻辑
	if len(transList) > 0:
		# 先计算出该返回的结果
		increase = (transList[-1].price - transList[0].price) / transList[0].price * 100
		# 基础数据的计算
		buyVolume = 1
		sellVolume = 1
		maxPrice = 0.0
		minPrice = 9999.0
		for trans in transList:
			if trans.type > 0:
				buyVolume += trans.volume
			elif trans.type < 0:
				sellVolume += trans.volume
			if trans.price > maxPrice:
				maxPrice = trans.price
			if trans.price < minPrice:
				minPrice = trans.price
		# 买盘比卖盘还少
		if forceShow == False and buyVolume < sellVolume:
			return increase
		# 振幅不到3%
		rangee = (maxPrice - minPrice) / transList[0].price * 100
		if forceShow == False and rangee < 3:
			return increase
		# 合并换手数据为分钟数据
		pass
		# 获得股票名称等数据
		stock = requestStockData(stockCode)
		while stock == False:
			stock = requestStockData(stockCode)
		# 跌幅已经超过5%
		if forceShow == False and stock.current < stock.yesterdayEnd * 0.95:
			return increase
		# 打印数据
		threadLock.acquire()
		print('==== ' + stockCode + ' ====')
		stock.printStockData()
		print('开收价: %.2f ~ %.2f 涨幅: %.2f%%' % (transList[0].price, transList[-1].price, increase))
		print('低高价: %.2f ~ %.2f 振幅: %.2f%%' % (minPrice, maxPrice, rangee))
		print('买卖比: %.1f%%' % (buyVolume * 100.0 / sellVolume))
		threadLock.release()
		# 检查打印完后的返回
		return increase
	else:
		return 0.0

def threadFunction(stockPrefix, start, end, step):
	for stockNumber in xrange(start, end, step):
		stockCode = '%s%06d' % (stockPrefix, stockNumber)
		while checkStockTrans(stockCode) == False:
			pass

if len(sys.argv) > 1:
	# 指定股票代码
	if len(sys.argv[1]) == 8 and (sys.argv[1].startswith('sh') or sys.argv[1].startswith('sz')) and sys.argv[1][2:8].decode().isdecimal():
		while checkStockTrans(sys.argv[1], True) == False:
			pass
	else:
		print('无效的股票代码')
else:
	# 多线循环筛选所有股票数据
	startTime = time.time()
	step = 50
	threadList = []
	for index in xrange(1, step):
		thread = threading.Thread(target = threadFunction, args = ('sz', 1 + index, 2784, step))
		thread.start()
		threadList.append(thread)
	for index in xrange(1, step):
		thread = threading.Thread(target = threadFunction, args = ('sh', 600000 + index, 603999, step))
		thread.start()
		threadList.append(thread)
	for thread in threadList:
		thread.join()
	print('总用时: %.2f秒' % (time.time() - startTime))
