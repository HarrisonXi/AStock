# -*- coding: utf-8 -*-
import requests
import os, sys
import re
import time
import threading

threadLock = threading.Lock()
step = 100
validPattern = re.compile(r'var hq_str_(s[hz]\d{6})="([^,"]+,){32}([^,"]+),?";')
# 确认存在的区间外特殊股票代码
validStockList = ['sz001696','sz001872','sz001896','sz001914','sz001965','sz001979','sz003816']

def filterStockList(stockList):
	url = 'https://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = requests.get(url, timeout = 3).text
	except requests.exceptions.RequestException:
		return False
	threadLock.acquire()
	match = validPattern.search(content)
	while match:
		if int(match.group(3)) == 0:
			validStockList.append(match.group(1))
		match = validPattern.search(content, match.end())
	threadLock.release()
	return True

def threadFunction(stockPrefix, start, end):
	stockList = []
	for stockNumber in range(start, end):
		stockCode = '{}{:06d}'.format(stockPrefix, stockNumber)
		stockList.append(stockCode)
	while filterStockList(stockList) == False:
		pass

# 多线循环筛选所有股票数据
startTime = time.time()
threadList = []
for index in range(1, 1000, step):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + step))
	threadList.append(thread)
for index in range(2001, 3000, step):
	thread = threading.Thread(target = threadFunction, args = ('sz', index, index + step))
	threadList.append(thread)
for index in range(600000, 602000, step):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + step))
	threadList.append(thread)
for index in range(603000, 604000, step):
	thread = threading.Thread(target = threadFunction, args = ('sh', index, index + step))
	threadList.append(thread)
for thread in threadList:
	thread.start()
for thread in threadList:
	thread.join()
validStockList.sort()
validStockFile = open(os.path.join(sys.path[0], 'stock.list'), 'w')
validStockFile.write('\n'.join(validStockList))
validStockFile.close()
print('总数量: {}'.format(len(validStockList)))
print('总用时: {:.2f}秒'.format(time.time() - startTime))
