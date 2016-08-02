# -*- coding: utf-8 -*-
import urllib2
import socket
import re
import time
import threading

threadLock = threading.Lock()
validPattern = re.compile(r'var hq_str_(s[hz]\d{6})="[^,"]+,[^,"]+,[^,"]+,[^,"]+,[^"]+";')
# 确认存在的3个特殊股票代码
validStockList = ["sz001696","sz001896","sz001979"]
# 2016年7月才上市的股票代码
newStockList = ["sz002803","sz002805","sz002806","sz002807","sz002808","sh600919","sh600936","sh600977","sh601595","sh601811","sh601966","sh601997","sh603007","sh603016","sh603069","sh603159","sh603322","sh603515","sh603569","sh603663","sh603843","sh603986"]

def filterStockList(stockList):
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return False
	except socket.timeout:
		return False
	threadLock.acquire()
	match = validPattern.search(content)
	while match:
		validStockList.append(match.group(1))
		match = validPattern.search(content, match.end() + 1)
	threadLock.release()
	return True

def threadFunction(stockPrefix, start, end):
	stockList = []
	for stockNumber in xrange(start, end):
		stockCode = '%s%06d' % (stockPrefix, stockNumber)
		stockList.append(stockCode)
	while filterStockList(stockList) == False:
		pass

# 多线循环筛选所有股票数据
startTime = time.time()
threadList = []
for index in xrange(1, 1000, 100):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + 100))
	threadList.append(thread)
for index in xrange(2001, 2809, 100):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + 100))
	threadList.append(thread)
for index in xrange(600000, 602000, 100):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + 100))
	threadList.append(thread)
for index in xrange(603000, 604000, 100):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + 100))
	threadList.append(thread)
for thread in threadList:
	thread.start()
for thread in threadList:
	thread.join()
for stockCode in newStockList:
	if stockCode in validStockList:
		validStockList.remove(stockCode)
validStockList.sort()
print("['" + "','".join(validStockList) + "']")
print('总数量: %d' % (len(validStockList)))
print('总用时: %.2f秒' % (time.time() - startTime))
