# -*- coding: utf-8 -*-
import urllib2
import socket
import os, sys
import re
import time
import threading

threadLock = threading.Lock()
validPattern = re.compile(r'var hq_str_(s[hz]\d{6})="[^,"]+,[^,"]+,[^,"]+,[^,"]+,[^"]+";')
# 确认存在的3个特殊股票代码
validStockList = ['sz001696','sz001896','sz001979']
# 2017年4月1日及之后才上市的股票代码
newStockList = ['sz002859','sz002860','sz002861','sz002862','sz002863','sz002865','sz002866','sz002867','sz002868','sz002869','sz002870','sz002871','sz002872','sz002873','sh601366','sh601952','sh603050','sh603078','sh603081','sh603086','sh603096','sh603113','sh603139','sh603180','sh603197','sh603225','sh603229','sh603232','sh603269','sh603320','sh603383','sh603385','sh603488','sh603501','sh603505','sh603538','sh603586','sh603680','sh603728','sh603758','sh603767','sh603787','sh603797','sh603803','sh603826','sh603855','sh603896','sh603906','sh603920','sh603926','sh603985']

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
for index in xrange(2001, 2874, 100):
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
