# -*- coding: utf-8 -*-
from termcolor import colored

class Stock:
	def __init__(self, name, todayStart, yesterdayEnd, current, highest = '0', lowest = '0'):
		self.name = name.decode('gbk').encode('utf-8')
		self.todayStart = float(todayStart)
		self.yesterdayEnd = float(yesterdayEnd)
		self.current = float(current)
		self.highest = float(highest)
		self.lowest = float(lowest)
		self.buyPercent = 0.0 # 买卖盘五档委比

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
			self.buyPercent = 2.0 * buyVolume / (buyVolume + sellVolume) - 1.0;

	def printStockData(self):
		# 停牌处理
		if self.todayStart == 0 or self.yesterdayEnd == 0:
			print('%s: 停牌' % (self.name))
			return
		# 计算现价显示的小数点位数
		if self.current < 10:
			priceStr = '%.3f' % self.current
		elif self.current < 100:
			priceStr = '%.2f' % self.current
		elif self.current < 1000:
			priceStr = '%.1f' % self.current
		else:
			priceStr = '%.0f' % self.current
		# 计算今日的涨跌幅
		if self.current < self.yesterdayEnd:
			increaseStr = '-%.2f%%' % ((self.yesterdayEnd - self.current) / self.yesterdayEnd * 100)
			increaseStr = colored(increaseStr, 'green')
		elif self.current > self.yesterdayEnd:
			increaseStr = '+%.2f%%' % ((self.current - self.yesterdayEnd) / self.yesterdayEnd * 100)
			increaseStr = colored(increaseStr, 'red')
		else:
			increaseStr = '0.00%'
		# 计算振幅及现价在今日振幅中的百分比位置
		swingRangeStr = ''
		swingPercentStr = ''
		if self.highest == 0 or self.lowest == 0:
			pass
		elif self.highest == self.lowest:
			swingRangeStr = ' 0.00%'
			if self.current < self.yesterdayEnd:
				swingPercentStr = ' 0.0'
			elif self.current > self.yesterdayEnd:
				swingPercentStr = ' 100.0'
			else:
				swingPercentStr = ' 50.0'
		else:
			swingRangeStr = ' %.2f%%' % ((self.highest - self.lowest) / self.yesterdayEnd * 100)
			swingPercentStr = ' %.1f' % ((self.current - self.lowest) / (self.highest - self.lowest) * 100)
		# 根据买卖盘委比给百分比数据着色
		if self.buyPercent < 0.2 and self.buyPercent > -0.2:
			pass
		elif self.buyPercent >= 0.8:
			swingPercentStr = colored(swingPercentStr + '+++', 'red')
		elif self.buyPercent >= 0.6:
			swingPercentStr = colored(swingPercentStr + '++', 'red')
		elif self.buyPercent >= 0.4:
			swingPercentStr = colored(swingPercentStr + '+', 'red')
		elif self.buyPercent >= 0.2:
			swingPercentStr = colored(swingPercentStr, 'red')
		elif self.buyPercent <= -0.8: 
			swingPercentStr = colored(swingPercentStr + '---', 'green')
		elif self.buyPercent <= -0.6: 
			swingPercentStr = colored(swingPercentStr + '--', 'green')
		elif self.buyPercent <= -0.4: 
			swingPercentStr = colored(swingPercentStr + '-', 'green')
		elif self.buyPercent <= -0.2: 
			swingPercentStr = colored(swingPercentStr, 'green')
		# 打印结果
		print('%s: %s %s%s%s' % (self.name, priceStr, increaseStr, swingRangeStr, swingPercentStr))

class Trans:
	def __init__(self, time = '00:00', volume = '0', price = '0', type = 'EQUAL'):
		self.time = int(time[0:2] + time[3:5])
		self.volume = int(volume)
		self.price = float(price)
		if type == 'DOWN':
			self.type = -1
		elif type == 'UP':
			self.type = 1
		else:
			self.type = 0

	def loadLine(self, line):
		params = line.split('\t')
		self.time = int(params[0])
		self.volume = int(params[1])
		self.price = float(params[2])
		self.type = int(params[3])

	def saveLine(self):
		return '%d\t%d\t%.3f\t%d\n' % (self.time, self.volume, self.price, self.type)

class Kline:
	def __init__(self, start = '0', highest = '0', lowest = '0', end = '0', volume = '0', date = '0', time = '00:00'):
		self.date = int(date.replace('-', ''))
		self.time = int(time[0:2] + time[3:5])
		self.start = float(start)
		self.end = float(end)
		self.highest = float(highest)
		self.lowest = float(lowest)
		self.volume = int(volume)
