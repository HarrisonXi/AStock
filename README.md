# AStock

A python script to monitor Chinese stocks in terminal. 一个在终端监视A股的python脚本。

## 使用示例

    python astock.py sh603019 sz002024

输出示例

![输出示例][1]

自动着色，最后一个参数=(现价-最低价)/(最高价-最低价)，用来指示现价在今日振幅中所处的百分比位置

## 自动补全

0字头股票代码脚本会自动补sz
6字头股票代码脚本会自动补sh

    python astock.py 603019 002024

等于

    python astock.py sh603019 sz002024

## 特殊代码

sh:上证指数
sz:深证指数

    python astock.py sh sz

等于

    python astock.py sh000001 sz399001


  [1]: https://raw.githubusercontent.com/HarrisonXi/AStock/master/output.png