# -*- coding: utf-8 -*-
from termcolor import colored

class Stock:
	def __init__(self, name, todayStart, yesterdayEnd, current, highest = '0', lowest = '0', buyPrice = '0', sellPrice = '0'):
		self.name = name.decode('gbk').encode('utf-8')
		self.todayStart = float(todayStart)
		self.yesterdayEnd = float(yesterdayEnd)
		self.current = float(current)
		self.highest = float(highest)
		self.lowest = float(lowest)
		self.buyPrice = float(buyPrice)
		self.sellPrice = float(sellPrice)

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
		# 计算现价在今日振幅中的百分比位置
		rangeStr = ''
		percentStr = ''
		if self.highest == 0 or self.lowest == 0:
			pass
		elif self.highest == self.lowest:
			rangeStr = ' 0.00%'
			if self.current < self.yesterdayEnd:
				percentStr = ' 0.0'
			elif self.current > self.yesterdayEnd:
				percentStr = ' 100.0'
			else:
				percentStr = ' 50.0'
		else:
			rangeStr = ' %.2f%%' % ((self.highest - self.lowest) / self.yesterdayEnd * 100)
			percentStr = ' %.1f' % ((self.current - self.lowest) / (self.highest - self.lowest) * 100)
		# 如果有买一卖一数据，给百分比数据着色
		if len(percentStr) == 0 or (self.sellPrice == 0 and self.buyPrice == 0):
			pass
		elif self.sellPrice == 0 and self.buyPrice > 0:
			percentStr = colored(percentStr, 'red')
		elif self.buyPrice > 0 and self.sellPrice == 0: 
			percentStr = colored(percentStr, 'green')
		elif self.sellPrice > self.buyPrice:
			if self.sellPrice <= self.current:
				percentStr = colored(percentStr, 'green')
			elif self.buyPrice >= self.current:
				percentStr = colored(percentStr, 'red')
		# 打印结果
		print('%s: %s %s%s%s' % (self.name, priceStr, increaseStr, rangeStr, percentStr))

class Trans:
	def __init__(self, time, volume, price, type):
		self.time = int(time.replace(':', ''))
		self.volume = int(volume)
		self.price = float(price)
		if type == 'DOWN':
			self.type = -1
		elif type == 'UP':
			self.type = 1
		else:
			self.type = 0
