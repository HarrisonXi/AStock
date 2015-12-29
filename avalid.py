# -*- coding: utf-8 -*-
import urllib2
import socket
import re
import time
import threading

threadLock = threading.Lock()
validStockList = []
validPattern = re.compile(r'var hq_str_(s[hz]\d{6})="[^,"]+,[^,"]+,[^,"]+,[^,"]+,[^"]+";')

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
for index in xrange(1, 2788, 100):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + 100))
	threadList.append(thread)
for index in xrange(600000, 604000, 100):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + 100))
	threadList.append(thread)
for thread in threadList:
	thread.start()
for thread in threadList:
	thread.join()
validStockList.sort()
print("['" + "','".join(validStockList) + "']")
print('总数量: %d' % (len(validStockList)))
print('总用时: %.2f秒' % (time.time() - startTime))
