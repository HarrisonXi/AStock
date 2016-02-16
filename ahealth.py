# -*- coding: utf-8 -*-
import urllib2
import socket
import re
import time
import threading
from aclass import *

threadLock = threading.Lock()
haltCount = 0
greatUpCount = 0
upCount = 0
equalCount = 0
downCount = 0
greatDownCount = 0
increase = 0.0
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^"]+";')

def devideStockList(stockList):
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	global haltCount
	global greatUpCount
	global upCount
	global equalCount
	global downCount
	global greatDownCount
	global increase
	threadLock.acquire()
	match = stockPattern.search(content)
	while match:
		stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4))
		if stock.todayStart == 0 or stock.yesterdayEnd == 0:
			haltCount += 1
		else:
			increase += (stock.current - stock.yesterdayEnd) / stock.yesterdayEnd * 100
			if stock.current > stock.yesterdayEnd * 1.06:
				greatUpCount += 1
			elif stock.current > stock.yesterdayEnd * 1.02:
				upCount += 1
			elif stock.current < stock.yesterdayEnd * 0.94:
				greatDownCount += 1
			elif stock.current < stock.yesterdayEnd * 0.98:
				downCount += 1
			else:
				equalCount += 1
		match = stockPattern.search(content, match.end() + 1)
	threadLock.release()
	return True

def threadFunction(stockPrefix, start, end):
	stockList = []
	for stockNumber in xrange(start, end):
		stockCode = '%s%06d' % (stockPrefix, stockNumber)
		stockList.append(stockCode)
	while devideStockList(stockList) == False:
		pass

# 多线循环筛选所有股票数据
startTime = time.time()
threadList = []
for index in xrange(1, 2789, 100):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + 100))
	threadList.append(thread)
for index in xrange(600000, 604000, 100):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + 100))
	threadList.append(thread)
for thread in threadList:
	thread.start()
for thread in threadList:
	thread.join()
totalCount = greatUpCount + upCount + equalCount + downCount + greatDownCount
localTime = time.localtime(startTime)
print('大涨数量: %d') % (greatUpCount)
print('小涨数量: %d') % (upCount)
print('稳定数量: %d') % (equalCount)
print('小跌数量: %d') % (downCount)
print('大跌数量: %d') % (greatDownCount)
print('平均涨幅: %.2f%%') % (increase / totalCount)
print('停牌数量: %d') % (haltCount)
print('总数量: %d') % (haltCount + totalCount)
print('开始时间: %02d:%02d:%02d' % (localTime.tm_hour, localTime.tm_min, localTime.tm_sec))
print('总用时: %.2f秒' % (time.time() - startTime))
