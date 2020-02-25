# -*- coding: utf-8 -*-
import os, sys
import pandas as pd
import numpy as np
from tkinter import *

# theme1
# bgColor = '#FFFFFF'
# redColor = '#FF0000'
# greenColor = '#00FF00'
# blueColor = '#0000FF'

# theme2
bgColor = '#DFDBC4'
redColor = '#990000'
greenColor = '#00A822'
blueColor = '#0C00AF'

offset = 3
maxPrice = None
minPrice = None
maxVolume = None
canvas = None

def drawCandle(df):
    global maxPrice
    global minPrice
    global maxVolume
    global canvas

    maxPrice = df.high.max()
    minPrice = df.low.min()
    maxVolume = df.vol.max()

    count = len(df.index)
    if count > 66:
        width = 1 + count * 6
    else:
        width = 400
    root = Tk()
    canvas = Canvas(root, width = width, height = 300, bg = bgColor)
    canvas.pack()

    drawLine(1, 247, width - 2, 247, blueColor)
    for i in range(count):
        s = df.iloc[i]
        drawPrice(i, s.open, s.high, s.low, s.close)
        drawVol(i, s.open, s.close, s.vol)

    mainloop()

def drawPrice(index, open, high, low, close):
    highY = 1 + int((maxPrice - high) / (maxPrice - minPrice) * 244)
    lowY = 1 + int((maxPrice - low) / (maxPrice - minPrice) * 244)
    openY = 1 + int((maxPrice - open) / (maxPrice - minPrice) * 244)
    closeY = 1 + int((maxPrice - close) / (maxPrice - minPrice) * 244)
    if close >= open:
        color = redColor
    else:
        color = greenColor
    drawLine(3 + index * 6, highY, 3 + index * 6, lowY, color)
    if openY == closeY:
        drawLine(1 + index * 6, openY, 5 + index * 6, closeY, color)
    else:
        drawRect(1 + index * 6, openY, 5 + index * 6, closeY, color)

def drawVol(index, open, close, vol):
    if close >= open:
        color = redColor
    else:
        color = greenColor
    startY = 298 - int(vol / maxVolume * 49)
    drawRect(1 + index * 6, startY, 5 + index * 6, 298, color)

def drawLine(x1, y1, x2, y2, color):
    canvas.create_line(x1 + offset, y1 + offset, x2 + offset, y2 + offset, fill = color)

def drawRect(x1, y1, x2, y2, color):
    canvas.create_rectangle(x1 + offset, y1 + offset, x2 + offset + 1, y2 + offset + 1, fill = color, width = 0)

if __name__ == '__main__':
    df = pd.read_csv(os.path.join(sys.path[0], 'test.csv'))
    print(df)
    drawCandle(df)
