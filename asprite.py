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
	stock.printStockData()
	return True

def compareStockTrans(trans1, trans2):
	return trans1.volume - trans2.volume

def checkStockTrans(stockCode):
	# 1小时最大数据量是1150左右，10分钟取个200
	url = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/CN_TransListV2.php?num=200&symbol=' + stockCode
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	# 抓取数据存入数组
	transList = []
	match = transPattern.search(content)
	while match:
		trans = Trans(match.group(1), match.group(2), match.group(3), match.group(4))
		transList.append(trans)
		match = transPattern.search(content, match.end() + 1)
	# 检查数据
	if False:
		while requestAndPrintStockData(stockCode) == False:
			pass
	return True

while True:
	for szCode in xrange(1, 2777, 10):
		stockCode = 'sz%06d' % (szCode)
		while checkStockTrans(stockCode) == False:
			pass
	for shCode in xrange(600000, 603999, 10):
		stockCode = 'sh%06d' % (shCode)
		while checkStockTrans(stockCode) == False:
			pass
