#coding=utf-8\
import sys
import urllib2
import re
import time

stockList = []
timePattern = re.compile(r',(\d+:\d+:\d+),')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}=\"([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),.+?\"')
lastTime = ''

def loadStockList():
	for index in range(1,len(sys.argv)):
		stockNumber = sys.argv[index];
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

def requestStockData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	content = urllib2.urlopen(url, timeout = 3).read()
	# 判断数据时间有没有更新
	global lastTime
	match = timePattern.search(content)
	if match.group(1) == lastTime:
		return
	lastTime = match.group(1)
	print(lastTime)
	# 循环抓取显示数据
	match = stockPattern.search(content)
	while match:
		print('%s 开盘:%s 昨收:%s 现价:%s 最高:%s 最低:%s' % (match.group(1).decode('gbk').encode('utf-8'), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6)))
		match = stockPattern.search(content, match.end() + 1)

if len(sys.argv) < 2:
	print('使用示例: python astock.py sh603019 sz002024\n自动补全：0字头股票代码脚本会自动补sz，6字头股票代码补sh\n特殊代码：sh-上证指数，sz-深证指数')
elif not loadStockList():
	print('没有有效的股票代码')
else:
	while True:
		requestStockData()
		time.sleep(6)
