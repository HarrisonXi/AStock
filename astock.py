#coding=utf-8\
import sys

stockList = []

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
	if len(stockList) == 0:
		return False
	return True

def requestData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	print url

if len(sys.argv) < 2:
	print '使用方法: python astock.py 000001 sh603019 sz002024'
elif not loadStockList():
	print '没有有效的股票代码'
else :
	requestData()