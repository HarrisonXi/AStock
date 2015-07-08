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
lastData = []

class Stock:
	def __init__(self, name, todayStart, yesterdayEnd, current, highest, lowest):
		self.name = name.decode('gbk').encode('utf-8')
		self.todayStart = float(todayStart)
		self.yesterdayEnd = float(yesterdayEnd)
		self.current = float(current)
		self.highest = float(highest)
		self.lowest = float(lowest)

def loadStockList():
	for index in range(1,len(sys.argv)):
		stockNumber = sys.argv[index]
		if len(stockNumber) == 8:
			# 8位长度的代码必须以sh或者sz开头
			if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
				stockList.append(stockNumber)
		elif len(stockNumber) == 6:
			if stockNumber.decode().isdigit():
				# 6位长度的0开头自动补sz，6开头补sh，3开头补sz
				if stockNumber.startswith('0'):
					stockList.append('sz' + stockNumber)
				elif stockNumber.startswith('6'):
					stockList.append('sh' + stockNumber)
				elif stockNumber.startswith('3'):
					stockList.append('sz' + stockNumber)
		elif stockNumber == 'sh':
			stockList.append('sh000001')
		elif stockNumber == 'sz':
			stockList.append('sz399001')
		elif stockNumber == 'cy':
			stockList.append('sz399006')
	if len(stockList) == 0:
		return False
	return True

def printStockData(stock):
	# 停牌处理
	if stock.todayStart == 0 or stock.yesterdayEnd == 0:
		print('%s:停牌' % (stock.name))
		return
	# 计算现价显示的小数点位数
	if stock.current < 1:
		priceStr = '%.4f' % stock.current
	elif stock.current < 10:
		priceStr = '%.3f' % stock.current
	elif stock.current < 100:
		priceStr = '%.2f' % stock.current
	elif stock.current < 1000:
		priceStr = '%.1f' % stock.current
	else:
		priceStr = '%.0f' % stock.current
	# 计算今日的涨跌幅
	if stock.current < stock.yesterdayEnd:
		increaseStr = '-%.2f%%' % ((stock.yesterdayEnd - stock.current) / stock.yesterdayEnd * 100)
		increaseStr = colored(increaseStr, 'green')
	elif stock.current > stock.yesterdayEnd:
		increaseStr = '+%.2f%%' % ((stock.current - stock.yesterdayEnd) / stock.yesterdayEnd * 100)
		increaseStr = colored(increaseStr, 'red')
	else:
		increaseStr = '0.00%'
	# 计算现价在今日振幅中的百分比位置
	if stock.highest == stock.lowest:
		if stock.current < stock.yesterdayEnd:
			percentStr = '0'
		elif stock.current > stock.yesterdayEnd:
			percentStr = '100'
		else:
			percentStr = '50'
	else:
		percentStr = '%.0f' % ((stock.current - stock.lowest) / (stock.highest - stock.lowest) * 100)
	# 打印结果
	print('%s:%s %s %s' % (stock.name, priceStr, increaseStr, percentStr))

def requestAllStockData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 5).read()
	except urllib2.URLError:
		return 1
	except socket.timeout:
		return 1
	# 判断数据时间有没有更新
	global lastTime
	match = timePattern.search(content)
	if match == None or match.group(1) == lastTime:
		return 2
	lastTime = match.group(1)
	# 循环抓取显示数据
	lastData[:] = []
	match = stockPattern.search(content)
	while match:
		lastData.append(Stock(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6)))
		match = stockPattern.search(content, match.end() + 1)
	return 0

if len(sys.argv) < 2:
	print('使用示例: python astock.py sh603019 sz002024\n自动补全：0字头股票代码脚本会自动补sz，6字头股票代码补sh\n特殊代码：sh-上证指数，sz-深证指数')
elif loadStockList() == False:
	print('没有有效的股票代码')
else:
	while True:
		result = requestAllStockData()
		if result == 0:
			print(lastTime)
			for stock in lastData:
				printStockData(stock)
			time.sleep(5)
		elif result == 1:
			print('超时重试')
		elif result == 2:
			time.sleep(5)
		else:
			print('未知错误')
			break
