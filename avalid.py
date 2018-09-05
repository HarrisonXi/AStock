# -*- coding: utf-8 -*-
import urllib2
import socket
import os, sys
import re
import time
import threading

threadLock = threading.Lock()
validPattern = re.compile(r'var hq_str_(s[hz]\d{6})="[^,"]+,[^,"]+,[^,"]+,[^,"]+,[^"]+";')
# 确认存在的4个特殊股票代码
validStockList = ['sz001696','sz001896','sz001965','sz001979']
# 2018年9月1日及之后才上市的股票代码
newStockList = ['sz002935','sz002936','sz002937','sz002938','sh601577','sh603297','sh603583','sh603790','sh603810']

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
		match = validPattern.search(content, match.end())
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
for index in xrange(2001, 3000, 100):
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
