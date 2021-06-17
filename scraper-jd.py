# -*- coding: utf-8 -*-

"""
JD online shopping helper tool
-----------------------------------------------------

only support to login by QR code, 
username / password is not working now.

"""
import importlib

import bs4
import requests, requests.utils, pickle
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

import os
import time
import datetime
import json
import random

import argparse
# from selenium import webdriver


import sys

importlib.reload(sys)

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name


def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''


def get_session():
    # 初始化session
    session = requests.session()
    # config:可以在订单结算页面打开调试模式，点击offline,然后点击提交，可以看到提交请求里有header信息
    session.headers = {"Accept": "application/json, text/javascript, */*; q=0.01",
                       "Content-Type": "application/x-www-form-urlencoded",
                       "Referer": "https://trade.jd.com/shopping/order/getOrderInfo.action",
                       "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
                       "sec-ch-ua-mobile": "?0",
                       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                       "X-Requested-With": "XMLHttpRequest"}

    # 获取cookies保存到session
    session.cookies = get_cookies()
    return session


def get_cookies():
    """解析cookies内容并添加到cookiesJar"""
    manual_cookies = {}
    # config:点击我的订单，在list.action请求header里就有cookie，全部复制过来
    cookies_String = "__jdu=173355604; shshshfpa=5aef2c23-ec49-146b-8226-94654a76ea5b-1609487674; shshshfpb=sFhS5FMMhSKWExo%2Fwag6mAw%3D%3D; user-key=eac0d4b0-d77b-4c03-9d69-23e05a8f9b7f; pinId=gbuozIL0gVzdZBi7Rs4WLbV9-x-f3wj7; pin=jd_527d68659371e; unick=%E5%8F%8C%E7%BC%9D%E5%B9%B2%E6%B6%89; ceshi3.com=103; _tp=BfyysksWTOR%2FCN3emITu97oIjXWDQPc1M%2BnigX2I4rc%3D; _pst=jd_527d68659371e; unpl=V2_ZzNtbRVTRRN3DkEAeUtfVWIGEw4RV0UVcAlCXXtOCwxlVxRZclRCFnUUR1NnGV0UZwUZXUFcQBRFCENkexhdBWMGEV5EVnMlMEsWBi8FXAduBBBaSl5LFXAJQFR5GFsGYjMRXXJWcxVzCkRQfx5dAFczElVGZ0MUdAlGVnMdXQFmAiKL7MOWncrR9vGts%2fLQ6rPH1OmD%2fZNFCE9UeRFdBGcEEW1DZ0IlI2ZGVXoYXQRmAxZbD1dFF3cMQlN6HGwEVwA%3d; __jdv=122270672|www.zhihu.com|t_1001542270_1001974758_0_1928410087|tuiguang|f577376e3c2a440bb17140581ff83e75|1623316341588; areaId=1; TrackID=17UgLX_KGhSgbxgXbBkdmU3IyE2Q53ur9ycwfHH9XuLv_d_VR93qEhjHL73he9jPgbagyD4FAY160C3SBf-cUQeGCPpXm9QmDu02jLkjYsXNCo2GwcHkbymJkMdzOEwkK; cn=4; __jda=122270672.173355604.1609487669.1623897772.1623932277.14; __jdc=122270672; shshshfp=c5bf8b11fdb56a89234a999250fcb092; ipLoc-djd=1-2800-2848-0.138360110; ipLocation=%u5317%u4eac; shshshsID=7882a1ab98fc43145e447576c4344a48_8_1623935392334; __jdb=122270672.13.173355604|14.1623932277; thor=EFFEB5852A25E247EA48E341B6EA045918D9992B3142A77E468598DB167DC90FEDC5F36740E3093483C3D3D50A01630C7230DC22513C984B71F82E11270E77C7A9A5746CF921556DFB0984C50E25A9FAD373750261D4408C2252DE8C40B0F800CE08C705B3E25F8AC08F54ACA5619D7A40B024AE049227AB085839F942AF48E7D7D5EE01AD91C134C61CCB253E51E526AFC1E17AA16C8BF4C6C749FB933F8D10; 3AB9D23F7A4B3C9B=OMU7GKPVTOYLCZ7NF5RQAJDKYJXRE6EEBNVGZQKXYP3F2KSJL2Y2CEYVOV4WWX6ZIAKOOTR4ZUIC34FX77T2GV24SE"
    for item in cookies_String.split(';'):
        name, value = item.strip().split('=', 1)
        # 用=号分割，分割1次
        manual_cookies[name] = value
        # 为字典cookies添加内容
    cookiesJar = requests.utils.cookiejar_from_dict(manual_cookies, cookiejar=None, overwrite=True)
    return cookiesJar


class JDWrapper(object):
    '''
    This class used to simulate login JD
    '''

    def __init__(self, usr_name=None, usr_pwd=None):
        # config:cookie info,eid和fp可以在订单结算页面打开调试模式，点击offline,然后点击提交，可以看到提交请求里有eip和fp
        self.eid = 'OMU7GKPVTOYLCZ7NF5RQAJDKYJXRE6EEBNVGZQKXYP3F2KSJL2Y2CEYVOV4WWX6ZIAKOOTR4ZUIC34FX77T2GV24SE'
        self.fp = 'f2b8a4bb0c96736674c946832d6527b4'

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.sess = get_session()

        self.cookies = {

        }

    @staticmethod
    def response_status(resp):
        if resp.status_code != requests.codes.OK:
            print('Status: %u, Url: %s' % (resp.status_code, resp.url))
            return False
        return True

    def good_stock(self, stock_id, good_count=1, area_id=None):
        '''
        33 : on sale, 
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        # stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        #   jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        stock_url = 'https://c0.3.cn/stocks'

        payload = {
            'type': 'getstocks',
            'skuIds': str(stock_id),
            'area': area_id or '1_72_2799_0',  # area change as needed
        }

        try:
            # get stock state
            resp = self.sess.get(stock_url, params=payload)
            if not self.response_status(resp):
                print(u'获取商品库存失败')
                return (0, '')

            # return json
            resp.encoding = 'gbk'
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info[stock_id]['StockState'])
            stock_stat_name = stock_info[stock_id]['StockStateName']

            # 33 : on sale, 34 : out of stock, 36: presell
            return stock_stat, stock_stat_name

        except Exception as e:
            print('Stocks Exception:', e)
            time.sleep(5)

        return (0, '')

    def good_detail(self, stock_id, area_id=None):
        # return good detail
        good_data = {
            'id': stock_id,
            'name': '',
            'link': '',
            'price': '',
            'stock': '',
            'stockName': '',
        }

        try:
            # shop page
            stock_link = 'http://item.jd.com/{0}.html'.format(stock_id)
            resp = self.sess.get(stock_link, verify=False)

            # good page
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # good name
            tags = soup.select('div#name h1')
            if len(tags) == 0:
                tags = soup.select('div.sku-name')
            good_data['name'] = tags_val(tags).strip(' \t\r\n')

            # cart link
            tags = soup.select('a#InitCartUrl')
            link = tags_val(tags, key='href')

            if link[:2] == '//': link = 'http:' + link
            good_data['link'] = link

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        # good price
        good_data['price'] = self.good_price(stock_id)

        # good stock
        good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=stock_id, area_id=area_id)
        # stock_str = u'有货' if good_data['stock'] == 33 else u'无货'

        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(u'{0} > 商品详情'.format(time.ctime()))
        print(u'编号：{0}'.format(good_data['id']))
        print(u'库存：{0}'.format(good_data['stockName']))
        print(u'价格：{0}'.format(good_data['price']))
        print(u'名称：{0}'.format(good_data['name']))
        # print(u'链接：{0}'.format(good_data['link'])

        return good_data

    def good_price(self, stock_id):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type': 1,
            'pduid': int(time.time() * 1000),
            'skuIds': 'J_' + stock_id,
        }

        price = '?'
        try:
            resp = self.sess.get(url, params=payload, verify=False)
            resp_txt = resp.text.strip()
            # print(resp_txt

            js = json.loads(resp_txt[1:-1])
            # print(u'价格', 'P: {0}, M: {1}'.format(js['p'], js['m'])
            price = js.get('p')

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return price

    def buy(self, options):
        # stock detail
        good_data = self.good_detail(options.good)

        # retry until stock not empty
        if good_data['stock'] != 33:
            # flush stock state
            while good_data['stock'] != 33 and options.flush:
                print(u'<%s> <%s>' % (good_data['stockName'], good_data['name']))
                time.sleep(options.wait / 1000.0)
                good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=options.good,
                                                                             area_id=options.area)

        # failed
        link = good_data['link']
        if good_data['stock'] != 33 or link == '':
            # print(u'stock {0}, link {1}'.format(good_data['stock'], link)
            return False

        try:
            # change buy count
            if options.count != 1:
                link = link.replace('pcount=1', 'pcount={0}'.format(options.count))

            # add to cart
            resp = self.sess.get(link, cookies=self.cookies, verify=False)
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # tag if add to cart succeed
            tag = soup.select('h3.ftx-02')
            if tag is None:
                tag = soup.select('div.p-name a')

            if tag is None or len(tag) == 0:
                print(u'添加到购物车失败')
                return False

            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(u'{0} > 购买详情'.format(time.ctime()))
            print(u'链接：{0}'.format(link))
            print(u'结果：{0}'.format(tags_val(tag)))

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))
        else:
            self.cart_detail()
            return self.order_info(options.submit)

        return False

    def cart_detail(self):
        # list all goods detail in cart
        cart_url = 'https://cart.jd.com/cart.action'
        cart_header = u'购买    数量    价格        总价        商品'
        cart_format = u'{0:8}{1:8}{2:12}{3:12}{4}'

        try:
            resp = self.sess.get(cart_url, cookies=self.cookies, verify=False)
            resp.encoding = 'utf-8'
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(u'{0} > 购物车明细'.format(time.ctime()))
            print(cart_header)

            for item in soup.select('div.item-form'):
                check = tags_val(item.select('div.cart-checkbox input'), key='checked')
                check = ' + ' if check else ' - '
                count = tags_val(item.select('div.quantity-form input'), key='value')
                price = tags_val(item.select('div.p-price strong'))
                sums = tags_val(item.select('div.p-sum strong'))
                gname = tags_val(item.select('div.p-name a'))
                #: ￥字符解析出错, 输出忽略￥
                print(cart_format.format(check, count, price[1:], sums[1:], gname))

            t_count = tags_val(soup.select('div.amount-sum em'))
            t_value = tags_val(soup.select('span.sumPrice em'))
            print(u'总数: {0}'.format(t_count))
            print(u'总额: {0}'.format(t_value[1:]))

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

    def order_info(self, submit=False):
        # get order info detail, and submit order
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(u'{0} > 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid': str(int(time.time() * 1000)),
            }

            # get preorder page
            rs = self.sess.get(order_url, params=payload, cookies=self.cookies, verify=False)
            soup = bs4.BeautifulSoup(rs.text, "html.parser")

            # order summary
            payment = tag_val(soup.find(id='sumPayPriceId'))
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = tag_val(detail.find(id='sendMobile'))
                snd_add = tag_val(detail.find(id='sendAddr'))

                print(u'应付款：{0}'.format(payment))
                print(snd_usr)
                print(snd_add)

            # just test, not real order
            if not submit:
                return False

            # config:order info,可以在订单结算页面打开调试模式，点击offline,然后点击提交，可以看到提交form data里有相关配置
            payload = {
                'overseaPurchaseCookies': '',
                'vendorRemarks': [],
                'submitOrderParam.sopNotPutInvoice': False,
                'submitOrderParam.trackID': 'TestTrackId',
                'presaleStockSign': 1,
                'submitOrderParam.ignorePriceChange': 0,
                'submitOrderParam.btSupport': 0,
                'submitOrderParam.eid': 'OMU7GKPVTOYLCZ7NF5RQAJDKYJXRE6EEBNVGZQKXYP3F2KSJL2Y2CEYVOV4WWX6ZIAKOOTR4ZUIC34FX77T2GV24SE',
                'submitOrderParam.fp': 'f2b8a4bb0c96736674c946832d6527b4',
                'submitOrderParam.jxj': 1
            }

            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action?&presaleStockSign=1'
            rp = self.sess.post(order_url, params=payload, cookies=self.cookies)

            if rp.status_code == 200:
                js = json.loads(rp.text)
                if js['success'] == True:
                    print(u'下单成功！订单号：{0}'.format(js['orderId']))
                    print(u'请前往东京官方商城付款')
                    return True
                else:
                    print(u'下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                print(u'请求失败. StatusCode:', rp.status_code)

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return False

    def login(self):
        for flag in range(1, 3):
            try:
                targetURL = 'https://order.jd.com/center/list.action'
                payload = {
                    'rid': str(int(time.time() * 1000)),
                }
                resp = self.sess.get(
                    url=targetURL, params=payload, allow_redirects=False, verify=False)
                if resp.status_code == requests.codes.OK:
                    print('校验是否登录[成功]')
                    return True
                else:
                    print('校验是否登录[失败]')
                    print('请重新输入cookie')
                    time.sleep(1)
                    continue
            except Exception as e:
                print(u'第【%s】次失败请重新获取cookie', flag)
                time.sleep(1)
                continue
        sys.exit(1)


def main(options):
    jd = JDWrapper()

    jd.login()
    # config:在此处配置购买的时间，若购买时间小于当前时间，则执行购买操作
    time1 = datetime.datetime(2021, 3, 16, 0, 0, 0, 250)
    while time1 >= datetime.datetime.now():
        print(u'时间记录{0}'.format(datetime.datetime.now()))
        time.sleep(options.wait / 2000.0)
    while not jd.buy(options) and options.flush:
        time.sleep(options.wait / 1000.0)


if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and buy sepecified good')
    # config:地址id，商品详情页，右键检查地址元素，data-localid就是area
    parser.add_argument('-a', '--area',
                        help='Area string, like: 1_72_2799_0 for Beijing', default='1-2800-2848-0')
    # config:商品id，需要进入商品详情页，地址栏的数字就是goodId
    parser.add_argument('-g', '--good',
                        help='Jing Dong good ID', default='10111164458')
    # config:抢购数量
    parser.add_argument('-c', '--count', type=int,
                        help='The count to buy', default=1)
    parser.add_argument('-w', '--wait',
                        type=int, default=500,
                        help='Flush time interval, unit MS')
    parser.add_argument('-f', '--flush',
                        action='store_true',
                        help='Continue flash if good out of stock')
    # config:default指定是否下单
    parser.add_argument('-s', '--submit',
                        action='store_true', default='true',
                        help='Submit the order to Jing Dong')

    options = parser.parse_args()
    print(options)

    main(options)
