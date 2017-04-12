# -*- coding: utf-8 -*-
import re
from termcolor import colored

asciiPattern = re.compile(r'[A-Z* ]')

# 实时数据Class
class Stock:
	def __init__(self, name, todayStart, yesterdayEnd, current, highest = '0', lowest = '0'):
		self.name = name.decode('gbk').encode('utf-8')
		self.todayStart = float(todayStart)
		self.yesterdayEnd = float(yesterdayEnd)
		self.current = float(current)
		self.highest = float(highest)
		self.lowest = float(lowest)
		self.buyPercent = 0.0 # 买卖盘五档委比

	# 计算买卖委比
	def calcBuyPercent(self, volumes):
		if len(volumes) < 10:
			return
		buyVolume = 0.0
		for index in range(0, 5):
			buyVolume += int(volumes[index])
		sellVolume = 0.0
		for index in range(5, 10):
			sellVolume += int(volumes[index])
		if buyVolume == 0 and sellVolume == 0:
			self.buyPercent = 0.0
		else:
			self.buyPercent = 2.0 * buyVolume / (buyVolume + sellVolume) - 1.0

	# 是否停牌的判断
	def isStop(self):
		return self.todayStart == 0 or self.yesterdayEnd == 0

	# 处理出对齐的名称（字符宽度为8个字母宽）
	def formattedName(self):
		asciiCount = len(asciiPattern.findall(self.name))
		nameWidth = (len(self.name) - asciiCount) / 3 * 2 + asciiCount
		return ' ' * (8 - nameWidth) + self.name

	# 打印股票数据
	def printStockData(self):
		# 停牌处理
		if self.isStop():
			print('%s:   停牌' % (self.formattedName()))
			return
		# 计算现价显示的小数点位数
		if self.current < 10:
			priceStr = '%6.3f' % self.current
		elif self.current < 100:
			priceStr = '%6.2f' % self.current
		elif self.current < 1000:
			priceStr = '%6.1f' % self.current
		else:
			priceStr = '%6.0f' % self.current
		# 计算今日的涨跌幅
		if self.current == self.yesterdayEnd:
			increaseStr = '  0.00%'
		else:
			increaseStr = '%+6.2f%%' % ((self.current - self.yesterdayEnd) / self.yesterdayEnd * 100)
			if self.current < self.yesterdayEnd:
				increaseStr = colored(increaseStr, 'green')
			else:
				increaseStr = colored(increaseStr, 'red')
		# 计算振幅及现价在今日振幅中的百分比位置
		swingRangeStr = ''
		swingPercentStr = ''
		if self.highest > 0 and self.lowest > 0:
			if self.highest == self.lowest:
				swingRangeStr = ' 0.00%'
				if self.current < self.yesterdayEnd:
					swingPercentStr = '  0'
				elif self.current > self.yesterdayEnd:
					swingPercentStr = '100'
				else:
					swingPercentStr = ' 50'
			else:
				swingRangeStr = '%5.2f%%' % ((self.highest - self.lowest) / self.yesterdayEnd * 100)
				swingPercentStr = '%3.0f' % ((self.current - self.lowest) / (self.highest - self.lowest) * 100)
		# 根据买卖盘委比给百分比数据加标记
		buyPercentStr = ''
		if self.buyPercent >= 0:
			buyPercentStr = colored('+' * int(self.buyPercent * 5.99), 'red')
		else:
			buyPercentStr = colored('-' * int(self.buyPercent * -5.99), 'green')
		# 打印结果
		print('%s: %s %s %s %s %s' % (self.formattedName(), priceStr, increaseStr, swingRangeStr, swingPercentStr, buyPercentStr))

# 换手数据Class
class Trans:
	def __init__(self, time = '00:00:00', volume = '0', price = '0', type = 'EQUAL'):
		self.time = int(time.replace(':', '')[0:4])
		self.volume = int(volume)
		self.price = float(price)
		if type == 'DOWN':
			self.type = -1
		elif type == 'UP':
			self.type = 1
		else:
			self.type = 0

# K线数据Class
class Kline:
	def __init__(self, start, highest, lowest, end, volume, dateTime = '1970-01-01 00:00:00'):
		params = dateTime.split(' ')
		self.date = int(params[0].replace('-', '')[-6:])
		if len(params) > 1:
			self.time = int(params[1].replace(':', '')[0:4])
		else:
			self.time = 1500
		self.start = float(start)
		self.end = float(end)
		self.highest = float(highest)
		self.lowest = float(lowest)
		self.volume = int(volume)
