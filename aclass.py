# -*- coding: utf-8 -*-
from termcolor import colored

class Stock:
	def __init__(self, name, todayStart, yesterdayEnd, current, highest, lowest):
		self.name = name.decode('gbk').encode('utf-8')
		self.todayStart = float(todayStart)
		self.yesterdayEnd = float(yesterdayEnd)
		self.current = float(current)
		self.highest = float(highest)
		self.lowest = float(lowest)

	def printStockData(self):
		# 停牌处理
		if self.todayStart == 0 or self.yesterdayEnd == 0:
			print('%s:停牌' % (self.name))
			return
		# 计算现价显示的小数点位数
		if self.current < 1:
			priceStr = '%.4f' % self.current
		elif self.current < 10:
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
		if self.highest == self.lowest:
			if self.current < self.yesterdayEnd:
				percentStr = '0'
			elif self.current > self.yesterdayEnd:
				percentStr = '100'
			else:
				percentStr = '50'
		else:
			percentStr = '%.0f' % ((self.current - self.lowest) / (self.highest - self.lowest) * 100)
		# 打印结果
		print('%s:%s %s %s' % (self.name, priceStr, increaseStr, percentStr))

class Trans:
	def __init__(self, time, volume, price, type):
		self.time = time
		self.volume = int(volume)
		self.price = float(price)
		if type == 'DOWN':
			self.type = -1
		elif type == 'UP':
			self.type = 1
		else:
			self.type = 0
