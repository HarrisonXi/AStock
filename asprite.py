# -*- coding: utf-8 -*-
import sys
import urllib2
import socket
import re
import time
from aclass import *

stockPattern = re.compile(r'var hq_str_s[hz]\d{6}=\"([^,]+),([^,]+),([^,]+),([^,]+),.+\"')
transPattern = re.compile(r'new Array\(\'([\d:]+)\', \'(\d+)\', \'([\d\.]+)\', \'(DOWN|UP|EQUAL)\'\)')

def requestAndPrintStockData(stockCode):
	url = 'http://hq.sinajs.cn/list=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	match = stockPattern.search(content)
	stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4))
	if stock.current >= stock.yesterdayEnd * 0.9666667:
		stock.printStockData()
	return True

def checkStockTrans(stockCode):
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
		buyVolume = 0
		sellVolume = 0
		for trans in transList:
			if trans.type > 0:
				buyVolume += trans.volume
			elif trans.type < 0:
				sellVolume += trans.volume
		if buyVolume > sellVolume * 1.5:
			while requestAndPrintStockData(stockCode) == False:
				pass
	return True

if len(sys.argv) > 1:
	while checkStockTrans(sys.argv[1]) == False:
		pass
else:
	for szCode in xrange(1, 2777):
		stockCode = 'sz%06d' % (szCode)
		while checkStockTrans(stockCode) == False:
			pass
	for shCode in xrange(600000, 603999):
		stockCode = 'sh%06d' % (shCode)
		while checkStockTrans(stockCode) == False:
			pass
