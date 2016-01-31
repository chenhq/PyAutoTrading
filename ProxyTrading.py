# -*- encoding: utf8 -*-

import datetime
import tushare as ts
from winguiauto import *

is_start = False
is_monitor = True
set_stock_info = []
order_msg = []
actual_stock_info = []
is_activated = [1] * 5  # 1：准备  0：交易成功 -1：交易失败


def findWantedControls(hwnd):
    # 获取双向委托界面level3窗体下所有控件句柄
    hwndChildLevel1 = dumpSpecifiedWindow(hwnd, wantedClass='AfxMDIFrame42s')
    print('hwndChildLevel1: ', hwndChildLevel1)
    hwndChildLevel2 = dumpSpecifiedWindow(hwndChildLevel1[0])
    print('hwndChildLevel2: ', hwndChildLevel2)
    for handler in hwndChildLevel2:
        hwndChildLevel3 = dumpSpecifiedWindow(handler)
        print('hwndChildLevel3: ', len(hwndChildLevel3), hwndChildLevel3)

        if len(hwndChildLevel3) == 73:  # 在hwndChildLevel3下，共有70个子窗体
            return hwndChildLevel3


def closePopupWindow(hwnd, wantedText=None, wantedClass=None):
    # 如果有弹出式窗口，点击它的确定按钮
    hwndPopup = findPopupWindow(hwnd)
    if hwndPopup:
        hwndControl = findControl(hwndPopup, wantedText, wantedClass)
        clickButton(hwndControl)
        time.sleep(1)
        return True
    return False


def buy(hwnd, stock_code, stock_number):
    pressKey(hwnd, win32con.VK_F6)
    hwndControls = findWantedControls(hwnd)
    if closePopupWindow(hwnd, wantedClass='Button'):
        time.sleep(5)
    click(hwndControls[2])
    time.sleep(.5)
    setEditText(hwndControls[2], stock_code)
    time.sleep(.5)
    click(hwndControls[7])
    time.sleep(.5)
    setEditText(hwndControls[7], stock_number)
    time.sleep(.5)
    clickButton(hwndControls[8])
    time.sleep(1)
    return not closePopupWindow(hwnd, wantedClass='Button')


def sell(hwnd, stock_code, stock_number):
    pressKey(hwnd, win32con.VK_F6)
    hwndControls = findWantedControls(hwnd)
    if closePopupWindow(hwnd, wantedClass='Button'):
        time.sleep(5)
    click(hwndControls[11])
    time.sleep(.5)
    setEditText(hwndControls[11], stock_code)
    time.sleep(.5)
    click(hwndControls[16])
    time.sleep(.5)
    setEditText(hwndControls[16], stock_number)
    time.sleep(.5)
    clickButton(hwndControls[17])
    time.sleep(1)
    return not closePopupWindow(hwnd, wantedClass='Button')


def order(hwnd_parent, stock_code, stock_number, trade_direction):
    if trade_direction == 'B':
        return buy(hwnd_parent, stock_code, stock_number)
    if trade_direction == 'S':
        return sell(hwnd_parent, stock_code, stock_number)


def tradingInit():
    # 获取交易软件句柄
    hwnd_parent = findSpecifiedTopWindow(wantedText=u'网上股票交易系统5.0')
    if hwnd_parent == 0:
        # TODO
        print(u'错误, 请先打开华泰证券交易软件，再运行本软件')
        return
    return hwnd_parent


def getStockData(items_info):
    code_name_price = []
    stock_codes = []
    for item in items_info:
        stock_codes.append(item[0])
    try:
        df = ts.get_realtime_quotes(stock_codes)
        for i in range(len(df)):
            code_name_price.append((df['code'][i], df['name'][i], float(df['price'][i])))
    except:
        return []
    # print(code_name_price)
    return code_name_price


def monitor():
    # 股价监控函数
    global actual_stock_info, order_msg, is_activated, set_stock_info

    hwnd = tradingInit()
    # 如果hwnd为零，直接终止循环
    while is_monitor and hwnd:
        time.sleep(3)
        if is_start:
            actual_stock_info = getStockData(set_stock_info)
            for actual_code, actual_name, actual_price in actual_stock_info:
                for row, (set_code, set_relation, set_price, set_direction, set_quantity, set_time) in enumerate(
                        set_stock_info):
                    if actual_code == set_code and actual_code and set_code \
                            and is_activated[row] == 1 and set_relation \
                            and set_direction and set_quantity and set_price > 0 \
                            and datetime.datetime.now().time() > set_time:
                        if set_relation == '>' and actual_price > set_price:
                            dt = datetime.datetime.now()
                            if order(hwnd, set_code, set_quantity, set_direction):
                                order_msg.append(
                                    (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                                     actual_name, set_direction,
                                     actual_price, set_quantity, '成功'))
                                is_activated[row] = 0
                            else:
                                order_msg.append(
                                    (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                                     actual_name, set_direction,
                                     actual_price, set_quantity, '失败'))
                                is_activated[row] = -1
                        if set_relation == '<' and actual_price < set_price:
                            dt = datetime.datetime.now()
                            if order(hwnd, set_code, set_quantity, set_direction):
                                order_msg.append(
                                    (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                                     actual_name, set_direction,
                                     actual_price, set_quantity, '成功'))
                                is_activated[row] = 0
                            else:
                                order_msg.append(
                                    (dt.strftime('%x'), dt.strftime('%X'), actual_code,
                                     actual_name, set_direction,
                                     actual_price, set_quantity, '失败'))
                                is_activated[row] = -1

