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
# 2017年11月1日及之后才上市的股票代码
newStockList = ['sz002864','sz002911','sz002912','sz002913','sz002915','sz002916','sz002917','sz002918','sz002919','sz002920','sh600025','sh600903','sh600933','sh601019','sh603076','sh603083','sh603161','sh603278','sh603283','sh603302','sh603365','sh603477','sh603507','sh603605','sh603659','sh603661','sh603685','sh603711','sh603809','sh603848','sh603856','sh603890','sh603912','sh603916','sh603917','sh603937','sh603970']

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
for index in xrange(2001, 2920, 100):
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
