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
# 2017年1月1日及之后才上市的股票代码
newStockList = ["sh603955","sh603178","sh603138","sz002851","sh603717","sh603578","sz002850","sh603388","sh603768","sh603238","sh603345","sh600939","sh603817","sh603603","sz002849","sh601212","sz002848","sh603615","sh603330","sh603208","sh603839","sh603626","sh603040","sh603637","sh603177","sz002847","sz002846","sh603360","sh603677","sh603881","sh603089","sh603358","sz002845","sh603966","sh603429","sz002839","sh601881","sh603638","sz002843","sh603037","sz002841","sh603337","sh601858","sh603165","sz002842","sh603668","sh603038","sh603690","sh603039","sz002824","sh603639","sh603579","sh603628","sh603266","sh603689","sh603877","sz002840","sh603228","sz002838","sh603035","sh603032","sh603186","sh603444"]

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
for index in xrange(2001, 2850, 100):
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
validStockFile = open(os.path.join(sys.path[0], 'stock.list'), 'w')
validStockFile.write('\n'.join(validStockList))
validStockFile.close()
print('总数量: %d' % (len(validStockList)))
print('总用时: %.2f秒' % (time.time() - startTime))
