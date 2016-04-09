# AStock

A python script to monitor Chinese stocks in terminal. 一个在终端监视A股的python脚本。

## 使用示例

    python astock.py sh600000 sz000001

输出示例

![输出示例][1]

自动着色。在涨跌幅后面的值是今日振幅。之后一个值=(现价-最低价)/(最高价-最低价)，用来指示现价在今日振幅中所处的百分比位置。最后一个值的颜色表示当前委比，红色表示委比大于20%，绿色表示委比小于-20%。

## 自动补全

6字头股票代码脚本会自动补sh

0字头股票代码脚本会自动补sz

3字头股票代码脚本会自动补sz

    python astock.py 600000 000001

等于

    python astock.py sh600000 sz000001

## 特殊代码

sh:上证指数

sz:深证指数

zx:中小板指

cy:创业板指

    python astock.py sh sz

等于

    python astock.py sh000001 sz399001

## 统计脚本

    python ahealth.py

输出示例

    大涨数量: 195
    小涨数量: 1545
    稳定数量: 188
    小跌数量: 2
    大跌数量: 10
    平均涨幅: 3.70%
    停牌数量: 354
    总数量: 2294
    开始时间: 10:46:01
    总用时: 0.30秒

不包含创业板股票，有需要的请自行添加。

## 关于

数据来源于新浪财经，代码库里有整理好的API文档。

如果有兴趣用python做真正的数据分析，可以去参考[TuShare开源库][2]，前往[TuShare主页][3]。

仅在Mac的python2.7环境下使用过，对其它平台的兼容没有测试过。

  [1]: https://raw.githubusercontent.com/HarrisonXi/AStock/master/output.png
  [2]: https://github.com/waditu/tushare
  [3]: http://pythonhosted.org/tushare/index.html
