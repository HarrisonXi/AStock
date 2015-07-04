#coding=utf-8\
import sys
import urllib2
import socket
import re
import time
from termcolor import colored

stockList = []
timePattern = re.compile(r',(\d+:\d+:\d+),')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}=\"([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),.+?\"')
lastTime = ''

def loadStockList():
	for index in range(1,len(sys.argv)):
		stockNumber = sys.argv[index]
		if len(stockNumber) == 8:
			# 8位长度的代码必须以sh或者sz开头
			if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
				stockList.append(stockNumber)
		elif len(stockNumber) == 6:
			if stockNumber.decode().isdigit():
				# 6位长度的0开头自动补sz，6开头的自动补sh
				if stockNumber.startswith('0'):
					stockList.append('sz' + stockNumber)
				elif stockNumber.startswith('6'):
					stockList.append('sh' + stockNumber)
		elif stockNumber == 'sh':
			stockList.append('sh000001')
		elif stockNumber == 'sz':
			stockList.append('sz399001')
	if len(stockList) == 0:
		return False
	return True

def printStockData(name, todayStart, yesterdayEnd, current, highest, lowest):
	# 停牌处理
	if todayStart == 0 or yesterdayEnd == 0:
		print('%s:停牌' % (name))
		return
	# 计算现价显示的小数点位数
	if current < 1:
		priceStr = '%.4f' % current
	elif current < 10:
		priceStr = '%.3f' % current
	elif current < 100:
		priceStr = '%.2f' % current
	elif current < 1000:
		priceStr = '%.1f' % current
	else:
		priceStr = '%.0f' % current
	# 计算今日的涨跌幅
	if current < yesterdayEnd:
		increaseStr = '-%.2f%%' % ((yesterdayEnd - current) / yesterdayEnd * 100)
		increaseStr = colored(increaseStr, 'green')
	elif current > yesterdayEnd:
		increaseStr = '+%.2f%%' % ((current - yesterdayEnd) / yesterdayEnd * 100)
		increaseStr = colored(increaseStr, 'red')
	else:
		increaseStr = '0.00%'
	# 计算现价在今日振幅中的百分比位置
	if highest == lowest:
		if current < yesterdayEnd:
			percentStr = '0'
		elif current > yesterdayEnd:
			percentStr = '100'
		else:
			percentStr = '50'
	else:
		percentStr = '%.0f' % ((current - lowest) / (highest - lowest) * 100)
	# 打印结果
	print('%s:%s %s %s' % (name, priceStr, increaseStr, percentStr))

def requestStockData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 5).read()
	except urllib2.URLError:
		print('超时重试')
		requestStockData()
		return
	except socket.timeout:
		print('超时重试')
		requestStockData()
		return
	# 判断数据时间有没有更新
	global lastTime
	match = timePattern.search(content)
	if match == None or match.group(1) == lastTime:
		return
	lastTime = match.group(1)
	print(lastTime)
	# 循环抓取显示数据
	match = stockPattern.search(content)
	while match:
		printStockData(match.group(1).decode('gbk').encode('utf-8'), float(match.group(2)), float(match.group(3)), float(match.group(4)), float(match.group(5)), float(match.group(6)))
		match = stockPattern.search(content, match.end() + 1)

if len(sys.argv) < 2:
	print('使用示例: python astock.py sh603019 sz002024\n自动补全：0字头股票代码脚本会自动补sz，6字头股票代码补sh\n特殊代码：sh-上证指数，sz-深证指数')
elif not loadStockList():
	print('没有有效的股票代码')
else:
	while True:
		requestStockData()
		time.sleep(5)
