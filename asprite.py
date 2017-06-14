# -*- coding: utf-8 -*-
import sys, os
import urllib2
import socket
import re
import time
import threading
from aclass import *

threadLock = threading.Lock()
dateTimePattern = re.compile(r',\d{2}(\d{2}-\d{2}-\d{2}),(\d{2}:\d{2}):\d{2},')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^,"]+,[^,"]+,([^,"]+),[^"]+";')
klinePattern = re.compile(r'\{day:"([\d\- :]+)",open:"([\d.]+)",high:"([\d.]+)",low:"([\d.]+)",close:"([\d.]+)",volume:"(\d+)"\}')
timePercent = 0 # 今天交易时间经过的百分比（例:午休=50%，14:00=75%）
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
		stock.volume = int(match.group(7))
	return stock

def requestStockData(stockCode):
	stock = requestStockData_(stockCode)
	while stock == False:
		stock = requestStockData_(stockCode)
	return stock

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
		match = klinePattern.search(content, match.end())
	return klineList

def requestKlineData(stockCode, count, scale = 240):
	klineList = requestKlineData_(stockCode, count, scale)
	while klineList == False:
		klineList = requestKlineData_(stockCode, count, scale)
	return klineList

def requestCorrectDate(expectedCount):
	klineList = requestKlineData('sh000001', expectedCount + 1)
	if klineList[-1].date == dateTime / 10000:
		return klineList[0].date
	else:
		return klineList[1].date

def scanStock(stockCode):
	pass

def threadFunction(stockList):
	for stockCode in stockList:
		scanStock(stockCode)

# 获取当前新浪服务器时间
dateTime = requestDateTime()
timePercent = calcTimePercent(dateTime)
correctDate = requestCorrectDate(5)
# 多线循环筛选所有股票数据
startTime = time.time()
if (os.path.isfile(os.path.join(sys.path[0], 'stock.list')) != True):
	print('请先运行avalid.py生成stock.list文件')
	exit(1)
validStockFile = open(os.path.join(sys.path[0], 'stock.list'), 'r')
validStockList = validStockFile.read().split('\n')
validStockFile.close()
countPerThread = (len(validStockList) + 99) / 100
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
