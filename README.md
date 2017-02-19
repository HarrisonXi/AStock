# AStock

A python script to monitor Chinese stocks in terminal. 一个在终端监视 A 股的 python 脚本。

### 使用示例

    python astock.py sh600000 sz000001

输出示例

![输出示例][1]

在涨跌幅后面的值是今日振幅。

后一个整数值 = (现价 - 最低价) / (最高价 - 最低价)，用来指示现价在今日振幅中所处的百分比位置。

最后的加号表示委比里委买多于委卖的数量，加号越多则委买的比例越高，最多 5 个加号。减号的意义可以类推。

### 自动补全

6 字头股票代码脚本会自动补 sh 前缀

0 字头股票代码脚本会自动补 sz 前缀

3 字头股票代码脚本会自动补 sz 前缀

    python astock.py 600000 000001

等于

    python astock.py sh600000 sz000001

### 特殊代码

sh: 上证指数

sz: 深证指数

zx: 中小板指

cy: 创业板指

300: 沪深300

    python astock.py sh sz

等于

    python astock.py sh000001 sz399001

### 统计脚本

    python ahealth.py

输出示例

![输出示例][4]

不包含创业板股票，有需要的请自行添加。

### 关于

数据来源于新浪财经，整理好的 API 文档：[实时行情API][5]、[历史行情API][6]

如果有兴趣用 python 做真正的数据分析，可以去参考[TuShare开源库][2]，前往[TuShare主页][3]。

仅在 Mac 的 python 2.7 环境下使用过，对其它平台的兼容没有测试过。

[1]: https://raw.githubusercontent.com/HarrisonXi/AStock/master/output1.png
[2]: https://github.com/waditu/tushare
[3]: http://pythonhosted.org/tushare/index.html
[4]: https://raw.githubusercontent.com/HarrisonXi/AStock/master/output2.png
[5]: https://github.com/HarrisonXi/AStock/blob/master/%E5%AE%9E%E6%97%B6%E8%A1%8C%E6%83%85API.md
[6]: https://github.com/HarrisonXi/AStock/blob/master/%E5%8E%86%E5%8F%B2%E6%95%B0%E6%8D%AEAPI.md