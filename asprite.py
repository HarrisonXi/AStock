# -*- coding: utf-8 -*-
import sys
import urllib2
import socket
import re
import time
import threading
from aclass import *

threadLock = threading.Lock()
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}=\"([^,]+),([^,]+),([^,]+),([^,]+),.+\"')
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
	# 抓取数据存入数组
	transList = []
	validTime = 0
	# maxVolume = 0
	# minVolume = 99999999
	maxPrice = 0
	minPrice = 9999
	match = transPattern.search(content)
	while match:
		trans = Trans(match.group(1), match.group(2), match.group(3), match.group(4))
		if validTime == 0:
			validTime = trans.time - 10000
		if trans.time >= validTime:
			# if trans.volume > maxVolume:
			# 	maxVolume = trans.volume
			# if trans.volume < minVolume:
			# 	minVolume = trans.volume
			if trans.price > maxPrice:
				maxPrice = trans.price
			if trans.price < minPrice:
				minPrice = trans.price
			transList.append(trans)
		match = transPattern.search(content, match.end() + 1)
	# 检查数据
	if len(transList) > 0:
		midPrice = (maxPrice + minPrice) * 0.5
		buyVolume = 0
		sellVolume = 0
		highCount = 0
		for trans in transList:
			if trans.type > 0:
				buyVolume += trans.volume
			elif trans.type < 0:
				sellVolume += trans.volume
			if trans.price > midPrice:
				highCount += 1
		passCheck = True
		if buyVolume < sellVolume * 1.333333:
			passCheck = False
		if highCount < len(transList) * 0.5:
			passCheck = False
		if transList[0].price < transList[-1].price:
			passCheck = False
		if forceShow or passCheck:
			stock = requestStockData(stockCode)
			while stock == False:
				stock = requestStockData(stockCode)
			if forceShow or stock.current >= stock.yesterdayEnd * 0.9666667:
				threadLock.acquire()
				print('==== ' + stockCode + ' ====')
				stock.printStockData()
				print('开始价: %.2f' % (transList[-1].price))
				print('最低价: %.2f' % (minPrice))
				print('最高价: %.2f' % (maxPrice))
				print('买量比: %.1f%%' % (buyVolume * 100.0 / sellVolume))
				print('高价比: %.1f%%' % (highCount * 100.0 / len(transList)))
				threadLock.release()
	return True

def threadFunction(stockPrefix, start, end, step):
	for stockNumber in xrange(start, end, step):
		stockCode = '%s%06d' % (stockPrefix, stockNumber)
		while checkStockTrans(stockCode) == False:
			pass

if len(sys.argv) > 1:
	if len(stockNumber) == 8 and (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
		while checkStockTrans(sys.argv[1], True) == False:
			pass
	else:
		print('无效的股票代码')
else:
	startTime = time.time()
	threadList = []
	step = 50
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
	print('cost: %.2fs' % (time.time() - startTime))
