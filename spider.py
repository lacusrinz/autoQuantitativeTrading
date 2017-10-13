# -*- coding: utf-8 -*-

import urllib
import requests
from selenium import webdriver
import time
import datetime
from bs4 import BeautifulSoup
import pymysql.cursors

# r = requests.get('http://quote.eastmoney.com/center/BKList.html#trade_0_0?sortRule=1')
#
# with open('/Users/RInz/Downloads/xx.htm', "wb") as code:
#     code.write(r.content)

url_hybkup = "http://quote.eastmoney.com/center/BKList.html#trade_0_0?sortRule=0"
url_hybkdown = "http://quote.eastmoney.com/center/BKList.html#trade_0_0?sortRule=1"
url_gnbkup = "http://quote.eastmoney.com/center/BKList.html#notion_0_0?sortRule=0"
url_gnbkdown = "http://quote.eastmoney.com/center/BKList.html#notion_0_0?sortRule=1"

url_10jqka = "http://q.10jqka.com.cn/thshy/"

bk_list_type_hybkup = 0
bk_list_type_hybkdown = 1
bk_list_type_gnbkup = 2
bk_list_type_gnbkdown = 3

def getHTML2DB(url, type, bk_name, conn):
    driver = webdriver.PhantomJS()
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
    driver.get(url)
    time.sleep(3)
    print 2
    file_name = "jpg/" + str(datetime.date.today())
    # file_name = "/usr/share/nginx/html/downloads/" + str(datetime.date.today())

    if 'eastmoney.com/center/BKList' in url:
        if type == bk_list_type_hybkup:
            file_name += "hybkup.jpg"
        elif type == bk_list_type_hybkdown:
            file_name += "hybkdown.jpg"
        elif type == bk_list_type_gnbkup:
            file_name += "gnbkup.jpg"
        elif type == bk_list_type_gnbkdown:
            file_name += "gnbkdown.jpg"

        # driver.get_screenshot_as_file(file_name)  # 获取页面截图
        # with open('/Users/RInz/Downloads/xx.htm', "wb") as code:
        #     code.write(r)

        r = driver.page_source.encode('gb2312', 'ignore')  # 这个函数获取页面的html
        driver.close()

        soup = BeautifulSoup(r)
        table = soup.find_all('table', attrs={'id': 'bklist'})

        trs = table[0].findAll('tr')
        for i in range(1, 11):
            tr = trs[i]
            tds = tr.findAll('td')
            # insertTableBKList(tds, type, conn)
            links = tds[1].findAll('a')
            list_url = links[0].get('href')
            print list_url
            getHTML2DB("http://quote.eastmoney.com/center/" + list_url, type, tds[1].getText(), conn)

    elif 'http://quote.eastmoney.com/center/list' in url:
        if type == bk_list_type_hybkup:
            file_name += "hybkup_list.jpg"
        elif type == bk_list_type_hybkdown:
            file_name += "hybkdown_list.jpg"
        elif type == bk_list_type_gnbkup:
            file_name += "gnbkup_list.jpg"
        elif type == bk_list_type_gnbkdown:
            file_name += "gnbkdown_list.jpg"

        # driver.get_screenshot_as_file(file_name)  # 获取页面截图

        r = driver.page_source.encode('gb2312', 'ignore')  # 这个函数获取页面的html
        driver.close()

        soup = BeautifulSoup(r)
        table = soup.find_all('table', attrs={'class': 'table-data'})
        trs = table[0].findAll('tr')
        for i in range(1, min(11, len(trs))):
            tr = trs[i]
            tds = tr.findAll('td')
            insertTableBKStocks(tds, type, bk_name, conn)

    elif 'http://q.10jqka.com.cn/thshy/detail/code' in url:
        file_name += "10JQKA_list.jpg"
        # driver.get_screenshot_as_file(file_name)  # 获取页面截图
        r = driver.page_source.encode('gbk', 'ignore')  # 这个函数获取页面的html
        driver.close()
        soup = BeautifulSoup(r)
        table = soup.find_all('tbody')
        trs = table[0].findAll('tr')
        print trs
        for i in range(0, min(10, len(trs))):
            tr = trs[i]
            tds = tr.findAll('td')
            insertTableHYStocks(tds, None, bk_name, conn)

    else:
        file_name += "10JQKA.jpg"
        print file_name
        # driver.get_screenshot_as_file(file_name)  # 获取页面截图
        r = driver.page_source.encode('gbk', 'ignore')  # 这个函数获取页面的html
        driver.close()
        soup = BeautifulSoup(r)
        table = soup.find_all('tbody')
        # print table
        trs = table[0].findAll('tr')
        print trs
        for i in range(0, 10):
            tr = trs[i]
            tds = tr.findAll('td')
            # insertTableHYList(tds, conn)
            links = tds[1].findAll('a')
            list_url = links[0].get('href')
            getHTML2DB(list_url, None, tds[1].getText(), conn)
    # driver.close()

def connDB():
    # Connect to the database
    connection = pymysql.connect(host='45.76.102.248',
                                 port=3306,
                                 user='root',
                                 password='123456654321',
                                 db='QuantitativeTrading',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def disconnDB(conn):
    conn.close()

def insertTableBKList(tds, bk_list_type, conn):
    sequence = int(tds[0].getText())
    bk_name = tds[1].getText()
    last_price = float(tds[3].getText())  # float(tds[1].getText().strip('%'))/100
    raise_down = float(tds[4].getText())
    raise_down_perc = float(tds[5].getText().strip('%')) / 100
    total_value = float(tds[6].getText())
    changes = float(tds[7].getText().strip('%')) / 100
    raise_num = int(tds[8].getText())
    down_num = int(tds[9].getText())
    top_raise_down = tds[10].getText()
    top_raise_down_perc = float(tds[11].getText().strip('%')) / 100

    collection_time = datetime.date.today()
    bk_list_type = bk_list_type

    connection = conn

    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            sql = 'INSERT INTO BKList (collection_time, bk_list_type, sequence, bk_name, last_price, raise_down, raise_down_perc, total_value, changes, raise_num, down_num, top_raise_down, top_raise_down_perc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            print sql
            cursor.execute(sql, (collection_time, bk_list_type, sequence, bk_name, last_price, raise_down, raise_down_perc, total_value, changes, raise_num, down_num, top_raise_down, top_raise_down_perc))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as err:
        print err
        disconnDB(conn)
    # finally:
    #     connection.close()

def insertTableHYList(tds, conn):
    sequence = int(tds[0].getText())
    bk_name = tds[1].getText()
    fluctuation = float(tds[2].getText()) / 100  # float(tds[1].getText().strip('%'))/100
    total_count = float(tds[3].getText())
    total_fee = float(tds[4].getText())
    net_incoming = float(tds[5].getText())
    up_count = int(tds[6].getText())
    down_count = int(tds[7].getText())
    average = float(tds[8].getText())
    top_name = tds[9].getText()
    price = float(tds[10].getText())
    top_fluctuation = float(tds[11].getText()) / 100

    collection_time = datetime.date.today()

    # Connect to the database
    connection = conn

    try:
        with connection.cursor() as cursor:
            sql = 'INSERT INTO HYList (collection_time, sequence, bk_name, fluctuation, total_count, total_fee, net_incoming, up_count, down_count, average, top_name, price, top_fluctuation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (
            collection_time, sequence, bk_name, fluctuation, total_count, total_fee, net_incoming,
            up_count, down_count, average, top_name, price, top_fluctuation))
        connection.commit()
    except Exception as err:
        print err
        disconnDB(conn)
    # finally:
    #     connection.close()

def insertTableBKStocks(tds, bk_list_type, bk_name, conn):
    print tds[4].getText()
    try float(tds[4].getText()):
        sequence = int(tds[0].getText())
        code = tds[1].getText()
        name = tds[2].getText()  # float(tds[1].getText().strip('%'))/100
        last_price = float(tds[4].getText())
        updown_price = float(tds[5].getText())
        updown_perc = float(tds[6].getText().strip('%')) / 100
        amplitude = float(tds[7].getText().strip('%')) / 100
        volumes_string = tds[8].getText()
        if u'万' in volumes_string:
            volumes = float(volumes_string.strip(u'万')) * 10000
        else:
            volumes = float(volumes_string)
        turnover_string = tds[9].getText()
        if u'万' in turnover_string:
            turnover = float(turnover_string.strip(u'万')) * 10000
        else:
            turnover = float(turnover_string)
        yesterday_end_price = float(tds[10].getText())
        today_open_price = float(tds[11].getText())
        highest = float(tds[12].getText())
        lowest = float(tds[13].getText())
        five_min = float(tds[14].getText().strip('%')) / 100
        bk_name = bk_name
        bk_list_type = bk_list_type

        collection_time = datetime.date.today()

        # # Connect to the database
        # connection = conn
        #
        print collection_time, bk_list_type, bk_name, sequence, code, name, last_price, updown_price, updown_perc, amplitude, volumes, turnover, yesterday_end_price, today_open_price, highest, lowest, five_min
        #
        # try:
        #     with connection.cursor() as cursor:
        #         sql = 'INSERT INTO BKStocks (collection_time, bk_list_type, bk_name, sequence, code, name, last_price, updown_price, updown_perc, amplitude, volumes, turnover, yesterday_end_price, today_open_price, highest, lowest, 5min) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        #         cursor.execute(sql, (
        #             collection_time, bk_list_type, bk_name, sequence, code, name, last_price, updown_price, updown_perc, amplitude, volumes, turnover, yesterday_end_price, today_open_price, highest, lowest, five_min))
        #     connection.commit()
        # except Exception as err:
        #     print err
        #     disconnDB(conn)

def insertTableHYStocks(tds, bk_name, conn):
    if tds[3].getText() is not '--':
        sequence = int(tds[0].getText())
        code = tds[1].getText()
        name = tds[2].getText()  # float(tds[1].getText().strip('%'))/100
        last_price = float(tds[3].getText())
        updown_price = float(tds[5].getText())
        updown_perc = float(tds[4].getText()) / 100
        speed = float(tds[6].getText()) / 100
        exchange = float(tds[7].getText()) / 100
        volume_ratio = float(tds[8].getText())
        amplitude = float(tds[9].getText()) / 100
        turnover = tds[10].getText()
        circulation_market_value = tds[12].getText()
        pe_ratio = tds[13].getText()
        bk_name = bk_name

        collection_time = datetime.date.today()

        # Connect to the database
        connection = conn

        print collection_time, bk_name, sequence, code, name, last_price, updown_price, updown_perc, speed, exchange, volume_ratio, amplitude, turnover, circulation_market_value, pe_ratio

        try:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO BKStocks (collection_time, bk_name, sequence, code, name, last_price, updown_price, updown_perc, speed, exchange, volume_ratio, amplitude, turnover, circulation_market_value, pe_ratio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (
                    collection_time, bk_name, sequence, code, name, last_price, updown_price, updown_perc, speed, exchange,
                    volume_ratio, amplitude, turnover, circulation_market_value, pe_ratio))
            connection.commit()
        except Exception as err:
            print err
            disconnDB(conn)


# conn = connDB()
# getHTML2DB(url_hybkup, bk_list_type_hybkup, None, conn)
# getHTML2DB(url_hybkdown, bk_list_type_hybkdown, None, conn)
# getHTML2DB(url_gnbkup, bk_list_type_gnbkup, None, conn)
# getHTML2DB(url_gnbkdown, bk_list_type_gnbkdown, None, conn)
# getHTML2DB(url_10jqka, None, None, conn)
# disconnDB(conn)

getHTML2DB('http://quote.eastmoney.com/center/list.html#28002729_0_2', bk_list_type_hybkdown, None, None)
