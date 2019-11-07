import json
import requests
from bs4 import BeautifulSoup as bs
import time
import codecs
import os
import datetime

#k python
import kinfo
import kvars


"""
剩下get twse 資訊
"""

def dictsortkeys(a):
    ''' 将字典转化为列表 '''
    keys = a.keys()
    vals = []
    
    for buf in keys:
        vals.append(buf)
        
    vals.sort()
    print(vals)
    return vals

#更新上市櫃代碼 
#Perfect
#CFIC Code要在確認  ******************
def update_list():    
    
    #一天更新一次
    if os.path.exists(kvars.STOCK_LIST_PATH) == True:
        file_t = time.localtime(os.path.getmtime(kvars.STOCK_LIST_PATH))
        local_t = time.localtime(time.time())
        if time.strftime("%Y%m%d",file_t) == time.strftime("%Y%m%d",local_t):
            print("Today already update stock number list.")
            return 1
    
    #更新上市代碼    
    no_res = requests.get(kvars.LIST_URL, auth=("user", "pass"))
    soup = bs(no_res.text)
    trs = soup.findAll("tr")
    f_stock = codecs.open(kvars.STOCK_LIST_PATH, "w", "big5", "ignore")
    f_stock.write("代號,股票名稱,上市櫃,產業別,\n")
    
    f_warrant = codecs.open(kvars.WARRANT_LIST_PATH, "w", "big5", "ignore")
    f_warrant.write("代號,權證名稱,C/P,上市櫃\n")
    for buf in trs:
        if "ESVUFR" in buf.text or "ESVTFR" in buf.text:
            tds = buf.findAll("td")
            #td[0] 是代號跟名稱, td[3]上市櫃 td[4] 是產業別
            f_stock.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",")
            f_stock.write(tds[3].text + "," + tds[4].text + ",\n")
        #順便更新權證代碼
        if "RWSCCA" in buf.text or "RWSCCE" in buf.text:
            tds = buf.findAll("td")
            f_warrant.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",0,")
            f_warrant.write(tds[3].text + "," + tds[4].text + ",\n")
        if "RWSCPE" in buf.text or "RWSCPA" in buf.text:
            tds = buf.findAll("td")
            f_warrant.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",1,")
            f_warrant.write(tds[3].text + "," + tds[4].text + ",\n")
    
    #更新上櫃代碼
    no_res = requests.get(kvars.OTC_LIST_URL, auth=("user", "pass"))
    soup = bs(no_res.text)
    trs = soup.findAll("tr")    
    for buf in trs:
        if "ESVUFR" in buf.text or "ESVTFR" in buf.text:
            tds = buf.findAll("td")
            #td[0] 是代號跟名稱, td[3]上市櫃 td[4] 是產業別
            f_stock.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",")
            f_stock.write(tds[3].text + "," + tds[4].text + ",\n")   
        #順便更新權證代碼
        if "RWSCCA" in buf.text or "RWSCCE" in buf.text:
            tds = buf.findAll("td")
            f_warrant.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",0,")
            f_warrant.write(tds[3].text + "," + tds[4].text + ",\n")
        if "RWSCPE" in buf.text or "RWSCPA" in buf.text:
            tds = buf.findAll("td")
            f_warrant.write(tds[0].text.split("\u3000")[0] + "," + tds[0].text.split("\u3000")[1] + ",1,")
            f_warrant.write(tds[3].text + "," + tds[4].text + ",\n")
    
    f_stock.close()
    f_warrant.close()
    del(no_res)
    del(soup)
    del(trs)
    print("Update stock number list finish.")
    
    return 0

#更新權值股
#要找出所有權值股, 之後可以連動指數
#Perfect
def update_power_list():
    
    #一天更新一次
    if os.path.exists(kvars.POWER_STOCK_LIST_PATH) == True:
        file_t = time.localtime(os.path.getmtime(kvars.POWER_STOCK_LIST_PATH))
        local_t = time.localtime(time.time())
        if time.strftime("%Y%m%d",file_t) == time.strftime("%Y%m%d",local_t):
            print("Today already update power stock number list.")
            return 1
    
    no_res = requests.get(kvars.POWER_URL, auth=("user", "pass"))
    no_res.encoding = "utf-8"
    soup = bs(no_res.text)
    divs = soup.findAll("div", {"id":"printhere"})
    f_power = codecs.open(kvars.POWER_STOCK_LIST_PATH, "w", "big5", "ignore")
    f_power.write("順序,代號,股票名稱,佔比,\n")
    
    for buf in divs:
        #print(buf)
        trs = buf.findAll("tr")
       
        for buf2 in trs:
            tds = buf2.findAll("td")
            for buf3 in tds:
                f_power.write(buf3.text.replace("\n","") + ",")
            #print(tds)
        #if "ESVUFR" in buf.text:
            #tds = buf.findAll("td")
            #print(tds)
            #td[0] 是代號跟名稱, td[3]上市櫃 td[4] 是產業別
            #print(tds)
            #print(len(tds.text))
            if len(tds) == 0:
                continue
            f_power.write("\n")
    f_power.close()
    
    f_power = codecs.open(kvars.POWER_STOCK_LIST_PATH, "r")
    f_power.readline()
    a = dict()
    for buf in f_power:
        buf2 = buf.replace("\n","").split(",")
        a[int(buf2[0])] = [buf2[1],buf2[2],buf2[3]]
        try:
            a[int(buf2[4])] = [buf2[5],buf2[6],buf2[7]]
        except:
            print("END")
    f_power.close()
    keysort = dictsortkeys(a)
    f_power = codecs.open(kvars.POWER_STOCK_LIST_PATH, "w") 
    f_power.write("順序,代號,股票名稱,佔比,\n")
    for buf in keysort:
        print(buf)
        f_power.write(str(buf)+","+a[buf][0]+","+a[buf][1]+","+a[buf][2]+",")
        f_power.write("\n")
    f_power.close()
    del(no_res)
    del(soup)
    del(trs)
    print("Update stock number list finish.")
    
    return 0

#檢查data檔案內的最後更新日期
#Perfect
def check_last_date(number):
    if os.path.exists("./data/" + str(number) + ".csv") == False:
        return 1992, 0, 0
    f = open("./data/" + str(number) + ".csv", "r")
    f.readline()
    year = 1992
    mon = 0
    day = 0
    for buf in f:
        buf2 = buf.split(",")
        year = int(buf2[0].split("/")[0]) + 1911
        mon =  int(buf2[0].split("/")[1])
        day =  int(buf2[0].split("/")[2])
    f.close()
    print("last update day = ", year, mon, day)
    return year,mon,day


#上市: "http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=19920802&stockNo=1102"
#上櫃: "http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=106/08&stkno=6173&_=1501848067399"
#***更新股票資料***
#number: 股票代碼
#isotc: 是不是OTC
#forceupdate: 有問題的時候利用此功能重新更新整支股票

#爬蟲爬出來的資料 =========
#stat, date, title, fields, data, notes
#設定waitt = 3, 是把更新太快, 會被證交所擋住
#Perfect
def update_stock(number, isotc, forceupdate=False):
    
    print("更新代碼 : " + str(number))
    
    #給定更新起始年月日
    yearstart, monstart, daystart = check_last_date(number)
    this_year = int(time.strftime("%Y"))+1 #+1是為了for迴圈連今年也要跑
    toyr, tomon = time.localtime(time.time()).tm_year, time.localtime(time.time()).tm_mon
    
    waitt = 3
    if forceupdate:
        yearstart, monstart, daystart = 1992, 0, 0
        waitt = 0.3 #這時候時間可以比較短, 因為真正有update東西的時候, 會有比較長的休息時間
        
    if forceupdate:
        f = open("./data/" + str(number) + ".csv", "w")
        f.write("time,open,high,low,close,turnover,volume\n")
    else:
        if os.path.exists("./data/" + str(number) + ".csv") == False:
            f = open("./data/" + str(number) + ".csv", "a")
            f.write("time,open,high,low,close,turnover,volume\n")
        else:
            f = open("./data/" + str(number) + ".csv", "a")
    
    #更新上市股票
    if isotc == False:
        for year in range(1992, this_year):
            if year < yearstart:
                continue
            for mon in range(1, 13):                
                if year <= yearstart and mon < monstart:
                    continue
                monstr = ""
                if mon < 10:
                    monstr = "0" + str(mon)
                else:
                    monstr = str(mon)
                
                if (year > toyr) or (year == toyr and mon > tomon):
                    continue
                print(year, mon)
                delayt = 1
                try:
                    r = requests.get("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number), auth=('user', 'pass'))
                    print("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number))
                    stockdata = json.loads(r.text)
                    time.sleep(waitt)
                except:
                    while True:
                        print ("except!!! no OK")
                        time.sleep(delayt)
                        try:
                            r = requests.get("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number), auth=('user', 'pass'))
                            stockdata = json.loads(r.text)
                            break
                        except:
                            delayt = delayt + 1
                        finally:
                            if delayt >= 11:
                                break
                finally:
                    #"0日期","1成交股數","2成交金額","3開盤價","4最高價","5最低價","6收盤價","7漲跌價差","8成交筆數"
                    if "OK" == stockdata["stat"]:
                        for i in range(0, len(stockdata["data"])):
                            if year <= yearstart and mon <= monstart and int(stockdata["data"][i][0].split("/")[2]) <= daystart:
                                continue
                            f.write(stockdata["data"][i][0].replace(",","") + "," + stockdata["data"][i][3].replace(",","") + "," + stockdata["data"][i][4].replace(",","") + "," + stockdata["data"][i][5].replace(",","") + "," + stockdata["data"][i][6].replace(",","") + "," + stockdata["data"][i][8].replace(",","")  + "," + stockdata["data"][i][1].replace(",","") + "\n")
                    else:
                        print ("ERROR no OK")
    #更新上櫃股票
    else:
        for year in range(2000, this_year):
            twyear = year - 1911
            if year < yearstart:
                continue
            #print (year)
            for mon in range(1, 13):                
                if year <= yearstart and mon < monstart:
                    continue
                monstr = ""
                if mon < 10:
                    monstr = "0" + str(mon)
                else:
                    monstr = str(mon)
                print(year, mon, toyr, tomon)
                if (year > toyr) or (year == toyr and mon > tomon):
                    continue
                
                delayt = 1
                try:
                    r = requests.get("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number), auth=('user', 'pass'))
                    print("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number))
                    stockdata = json.loads(r.text)                    
                    time.sleep(waitt)
                except:
                    while True:
                        print ("except!!! no OK")
                        time.sleep(delayt)
                        try:
                            r = requests.get("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number), auth=('user', 'pass'))
                            stockdata = json.loads(r.text)                    
                            break
                        except:
                            delayt = delayt + 1
                        finally:
                            if delayt >= 11:
                                break
                finally:
                    #print(stockdata["aaData"]) 0: date, 1: Vol, 3:Open, 4: H, 5: L, 6: C 8: Turnover
                    if int(stockdata["iTotalRecords"]) > 0:
                        for i in range(0, len(stockdata["aaData"])):
                            if year <= yearstart and mon <= monstart and int(stockdata["aaData"][i][0].replace("＊","").split("/")[2]) <= daystart:
                                continue
                            f.write(stockdata["aaData"][i][0].replace("＊","").replace(",","") + "," + stockdata["aaData"][i][3].replace(",","") + "," + stockdata["aaData"][i][4].replace(",","") + "," + stockdata["aaData"][i][5].replace(",","") + "," + stockdata["aaData"][i][6].replace(",","") + "," + stockdata["aaData"][i][8].replace(",","") + "," + stockdata["aaData"][i][1].replace(",","") + "\n")
                    else:
                        print ("ERROR no OK")
    f.close()


#TXF
#http://www.taifex.com.tw/chinese/3/3_1_1.asp?syear=2017&smonth=11&sday=2&commodity_id=TX
#http://www.taifex.com.tw/chinese/3/3_1_1_tbl.asp?syear=2017&smonth=11&sday=2&commodity_id=TX
#Perfect
def update_txf(forceupdate=False):
        
    this_year = int(time.strftime("%Y"))+1 #+1是為了for迴圈
    this_mon = int(time.strftime("%m"))
    this_day = int(time.strftime("%d"))
    print(this_mon)
    start_year = 2000
    start_mon = 0
    start_day = 0
    if forceupdate == True:
        start_year = 2000
        start_mon = 0
        start_day = 0
        f_txf = open(kvars.TXF_PATH,"w")
        f_txf.write("日期,開,高,低,收,成交量,未沖銷,\n")
    else:
        if os.path.exists(kvars.TXF_PATH):
            f_txfr = open(kvars.TXF_PATH, "r")
            f_txfr.readline()
            for buf in f_txfr:
                buf2 = buf.split(",")[0]
                
                if len(buf2) < 2:
                    break
                
                start_year, start_mon, start_day = int(buf2.split("/")[0]), int(buf2.split("/")[1]), int(buf2.split("/")[2])
            #print(start_year, start_mon, start_day)
            f_txfr.close()
            f_txf = open(kvars.TXF_PATH, "a")
        else:
            f_txf = open(kvars.TXF_PATH,"w")
            f_txf.write("日期,開,高,低,收,成交量,未沖銷,\n")
    #yr = 2017
    #mon = 11
    #day = 3
    for yr in range(start_year, this_year):
        if yr < start_year:
            continue
        for mon in range(1, 13):
            if yr == start_year and mon < start_mon:
                continue
            #print(yr,this_year,mon,this_mon)
            if yr == this_year-1 and mon > this_mon:
                break
            for day in range(1, 32):
                print(yr,mon,day)
                if yr == start_year and mon == start_mon and day <= start_day:
                    continue
                if yr == this_year and mon == start_mon and day > this_day:
                    break
                try:
                    r = requests.get("http://www.taifex.com.tw/chinese/3/3_1_1_tbl.asp?syear=" + str(yr) + "&smonth=" + str(mon) + "&sday=" + str(day) + "&commodity_id=TX", auth=('user', 'pass'))
                    r.encoding = "utf-8"
                    if "日期：" in r.text:
                        htmly,htmlm,htmld = r.text.split("日期：")[1].split("</h3>")[0].split("/")[0],r.text.split("日期：")[1].split("</h3>")[0].split("/")[1],r.text.split("日期：")[1].split("</h3>")[0].split("/")[2]
                        if int(htmly) != yr or int(htmlm) != mon or int(htmld) != day:
                            print(yr,mon,day)
                            time.sleep(3)
                            continue
                    soup = bs(r.text)
                    tbody = soup.findAll("tbody")
                    if (len(tbody)) == 0:
                        continue
                    
                    trs1 = tbody[0].findAll("tr")
                    tds1 = trs1[1].findAll("td")
                    t1turnover = int(tds1[10].text)
                    #print(trs1[1])
                    
                    trs2 = tbody[0].findAll("tr")
                    tds2 = trs2[2].findAll("td")
                    t2turnover = int(tds2[10].text)
        
                    if t1turnover >= t2turnover:
                        f_txf.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds1[2].text+","+tds1[3].text+","+tds1[4].text+","+tds1[5].text+","+tds1[10].text+","+tds1[12].text+",\n")
                    else:
                        f_txf.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds2[2].text+","+tds2[3].text+","+tds2[4].text+","+tds2[5].text+","+tds2[10].text+","+tds2[12].text+",\n")
                except:
                    looptime = 0
                    while looptime < 10:
                        print ("except!!! no OK")
                        r = requests.get("http://www.taifex.com.tw/chinese/3/3_1_1_tbl.asp?syear=" + str(yr) + "&smonth=" + str(mon) + "&sday=" + str(day) + "&commodity_id=TX", auth=('user', 'pass'))
                        r.encoding = "utf-8"
                        if "日期：" in r.text:
                            htmly,htmlm,htmld = r.text.split("日期：")[1].split("</h3>")[0].split("/")[0],r.text.split("日期：")[1].split("</h3>")[0].split("/")[1],r.text.split("日期：")[1].split("</h3>")[0].split("/")[2]
                            if int(htmly) != yr or int(htmlm) != mon or int(htmld) != day:
                                print(yr,mon,day)
                                time.sleep(3)
                                continue
                        soup = bs(r.text)
                        tbody = soup.findAll("tbody")
                        
                        if (len(tbody)) == 0:
                            continue
                        
                        trs1 = tbody[0].findAll("tr")
                        tds1 = trs1[1].findAll("td")
                        t1turnover = int(tds1[10].text)
                        #print(trs1[1])
                        
                        trs2 = tbody[0].findAll("tr")
                        tds2 = trs2[2].findAll("td")
                        t2turnover = int(tds2[10].text)
                        #print(t1turnover, t2turnover)
                        if t1turnover >= t2turnover:
                            f_txf.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds1[2].text+","+tds1[3].text+","+tds1[4].text+","+tds1[5].text+","+tds1[10].text+","+tds1[12].text+",\n")
                        else:
                            f_txf.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds2[2].text+","+tds2[3].text+","+tds2[4].text+","+tds2[5].text+","+tds2[10].text+","+tds2[12].text+",\n")
                        time.sleep(5+looptime)
                        looptime = looptime + 1
                time.sleep(1)
    f_txf.close()

#TWSE
#http://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=json&date=20171003&_=1509877490919 開高低收
#http://www.twse.com.tw/zh/page/trading/exchange/FMTQIK.html 成交量
def load_twse():
    pass

#目前issue都解了, 暫時不使用
#True 代表data是好的
#False代表data是壞的
#Perfect
def check_data(number, isotc):
    #幾種issue
    #1. data重複
    #2. 時間跳過  2目前無解法    
    f = open("./data/" + str(number) + ".csv", "r")
    f.readline()
    tempbuf = []
    for buf in f:
        if not buf:
            break
        if buf in tempbuf:
            return False
        tempbuf.append(buf)    
    f.close()
    
    return True

#不會每天更新   要想多久更新一次  一個月之類的
#3是除息日 4是除息參考價 5是除權日 6是除權參考價 10是現金股利 13是股票股利
#Perfect
def get_adj_close(num):
    # Request HTML information
    #a = input('For retrieving ex-right & ex-dividend information, enter the stock number in 4 digits: ')
    print(num)
    if os.path.exists("./adjclose/"+str(num)+".csv"):    
        file_t = time.localtime(os.path.getmtime("./adjclose/"+str(num)+".csv"))
        local_t = time.localtime(time.time())
        if time.strftime("%Y%m",file_t) == time.strftime("%Y%m",local_t):
            return
    session = requests.Session()
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    url = "https://goodinfo.tw/StockInfo/StockDividendSchedule.asp?STOCK_ID={}".format(num)
    req = session.get(url, headers=headers)
    req.encoding = 'utf-8'
    
    # Pull data out of HTML
    soup = bs(req.text, 'html.parser')
    #print(soup)
    try:
        stock_title = soup.select("title")[0].text
        
        if not soup.select("#divDetail"):
            print("The stock you entered has no such information.")
        
        else:
            tabledatasaved = ""
            for data in soup.select("#divDetail"):
                for data_tr in data.find_all('tr'):
                    tabledata = ""
                    for data_td in data_tr.find_all('td'):
                        tabledata = tabledata + "," + data_td.text
                    #print("1",tabledata)
                    if "0" not in tabledata:
                        continue
                    #print("2",tabledata)
                    tabledatasaved = tabledatasaved + "\n" + tabledata[1:]
            with open(os.path.expanduser("./adjclose/{}.csv").format(stock_title[1:5]),"w") as file:
                file.write("盈餘年度,股利發放年度,股東會日期,除息交易日,除息參考價,除權交易日,除權參考價,現金股利發放日,現金盈餘,現金公積,現金合計,股票盈餘,股票公積,股票合計,股利合計,發放年度平均股價,年均殖利率,")
            #print(tabledatasaved[120:])
            #if "0" in tabledatasaved:
                # Write to a csv file
            with open(os.path.expanduser("./adjclose/{}.csv").format(stock_title[1:5]),"ab") as file:
                file.write(bytes(tabledatasaved, encoding='utf-8', errors='ignore'))
            
            print("Exported csv successfully!".format(stock_title[:10]))
    except:
        pass
    time.sleep(60)    

#http://www.twse.com.tw/exchangeReport/MI_MARGN?response=html&date=20180426&selectType=MS
#融資券餘額
def update_credit():
    this_year = int(time.strftime("%Y"))+1 #+1是為了for迴圈
    this_mon = int(time.strftime("%m"))
    this_day = int(time.strftime("%d"))
    start_year = 2002
    start_mon = 1
    start_day = 1
    if os.path.exists("./data/credit.csv"):    
        f_credit = open("./data/credit.csv", "r")
        f_credit.readline()
        for buf in f_credit:
            buf2 = buf.split(",")[0]
            
            if len(buf2) < 2:
                break
            
            start_year, start_mon, start_day = int(buf2.split("/")[0]), int(buf2.split("/")[1]), int(buf2.split("/")[2])
        #print(start_year, start_mon, start_day)
        f_credit.close()
        f_credit = open("./data/credit.csv", "a")
    else:
        f_credit = open("./data/credit.csv", "a")
        f_credit.write("日期,融資買金額(千元),賣出,現金償還,前日餘額,今日餘額,融券買,賣出,現券償還,前日餘額,今日餘額,\n")
    for yr in range(start_year, this_year):
        if yr < start_year:
            continue
        for mon in range(1, 13):
            if yr == start_year and mon < start_mon:
                continue
            #print(yr,this_year,mon,this_mon)
            if yr == this_year-1 and mon > this_mon:
                break
            smon = ""
            if mon < 10:
                smon = "0" + str(mon)
            else:
                smon = str(mon)
            for day in range(1, 32):
                #print(yr,mon,day)
                
                if yr == start_year and mon == start_mon and day <= start_day:
                    continue
                if yr == this_year and mon == start_mon and day > this_day:
                    break
                sday = ""
                if day < 10:
                    sday = "0" + str(day)
                else:
                    sday = str(day)
                try:
                    print("http://www.twse.com.tw/exchangeReport/MI_MARGN?response=html&date=" + str(yr) + smon + sday + "&selectType=MS")
                    r = requests.get("http://www.twse.com.tw/exchangeReport/MI_MARGN?response=html&date=" + str(yr) + smon + sday + "&selectType=MS", auth=('user', 'pass'))
                    #print("http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=" + str(yr) + "/" + str(mon) + "/" + str(day) + "&dateend=" + str(yr) + "/" + str(mon) + "/" + str(day))
                    r.encoding = "utf-8"
                    
                    soup = bs(r.text)
                    
                    tbody = soup.findAll("table")
                    
                    if (len(tbody)) == 0:
                        continue
                    
                    trs1 = tbody[0].findAll("tr")
                    if len(trs1) < 3:
                        continue
                    tds1 = trs1[2].findAll("td")
                    if len(tds1) == 0:
                        continue
                    tds2 = trs1[3].findAll("td")
                    if len(tds2) == 0:
                        continue
                    #print(tds[3].text)
                    
        
                    f_credit.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds2[1].text.replace(",","")+","+tds2[2].text.replace(",","")+","+tds2[3].text.replace(",","")+","+tds2[4].text.replace(",","")+","+tds2[5].text.replace(",","")+","+tds1[1].text.replace(",","")+","+tds1[2].text.replace(",","")+","+tds1[3].text.replace(",","")+","+tds1[4].text.replace(",","")+","+tds1[5].text.replace(",","")+",\n")
                except:
                    looptime = 0
                    while looptime < 10:
                        print ("except!!! no OK")
                        r = requests.get("http://www.twse.com.tw/exchangeReport/MI_MARGN?response=html&date=" + str(yr) + smon + sday + "&selectType=MS", auth=('user', 'pass'))
                        
                        r.encoding = "utf-8"
                        
                        soup = bs(r.text)
                        
                        tbody = soup.findAll("table")
                        
                        if (len(tbody)) == 0:
                            continue
                        
                        trs1 = tbody[0].findAll("tr")
                        if len(trs1) < 3:
                            continue
                        tds1 = trs1[2].findAll("td")
                        if len(tds1) == 0:
                            continue
                        tds2 = trs1[3].findAll("td")
                        if len(tds2) == 0:
                            continue
                        #print(tds[3].text)
                        
            
                        f_credit.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds2[1].text.replace(",","")+","+tds2[2].text.replace(",","")+","+tds2[3].text.replace(",","")+","+tds2[4].text.replace(",","")+","+tds2[5].text.replace(",","")+","+tds1[1].text.replace(",","")+","+tds1[2].text.replace(",","")+","+tds1[3].text.replace(",","")+","+tds1[4].text.replace(",","")+","+tds1[5].text.replace(",","")+",\n")
                        time.sleep(5+looptime)
                        looptime = looptime + 1
                time.sleep(5)
    f_credit.close()

#start from 2001/01/01
#http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=2002/1/2&dateend=2002/1/2
#Put/Call Ratio
#Start from 2002/01/01
def update_pcr():
    this_year = int(time.strftime("%Y"))+1 #+1是為了for迴圈
    this_mon = int(time.strftime("%m"))
    this_day = int(time.strftime("%d"))
    start_year = 2002
    start_mon = 1
    start_day = 1
    if os.path.exists("./data/pcr.csv"):    
        f_pcr = open("./data/pcr.csv", "r")
        f_pcr.readline()
        for buf in f_pcr:
            buf2 = buf.split(",")[0]
            
            if len(buf2) < 2:
                break
            
            start_year, start_mon, start_day = int(buf2.split("/")[0]), int(buf2.split("/")[1]), int(buf2.split("/")[2])
        #print(start_year, start_mon, start_day)
        f_pcr.close()
        f_pcr = open("./data/pcr.csv", "a")
    else:
        f_pcr = open("./data/pcr.csv", "a")
        f_pcr.write("日期	,賣權成交量,買權成交量,買賣權成交量比率%,賣權未平倉量,買權未平倉量,買賣權未平倉量比率%,\n")
    for yr in range(start_year, this_year):
        if yr < start_year:
            continue
        for mon in range(1, 13):
            if yr == start_year and mon < start_mon:
                continue
            #print(yr,this_year,mon,this_mon)
            if yr == this_year-1 and mon > this_mon:
                break
            for day in range(1, 32):
                print(yr,mon,day)
                if yr == start_year and mon == start_mon and day <= start_day:
                    continue
                if yr == this_year and mon == start_mon and day > this_day:
                    break
                try:
                    r = requests.get("http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=" + str(yr) + "/" + str(mon) + "/" + str(day) + "&dateend=" + str(yr) + "/" + str(mon) + "/" + str(day), auth=('user', 'pass'))
                    #print("http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=" + str(yr) + "/" + str(mon) + "/" + str(day) + "&dateend=" + str(yr) + "/" + str(mon) + "/" + str(day))
                    r.encoding = "utf-8"
                    if "日期：" in r.text:
                        htmly,htmlm,htmld = r.text.split("日期：")[1].split("</h3>")[0].split("/")[0],r.text.split("日期：")[1].split("</h3>")[0].split("/")[1],r.text.split("日期：")[1].split("</h3>")[0].split("/")[2]
                        if int(htmly) != yr or int(htmlm) != mon or int(htmld) != day:
                            print(yr,mon,day)
                            time.sleep(3)
                            continue
                    soup = bs(r.text)
                    
                    tbody = soup.findAll("table", {"class":"table_a"})
                    
                    if (len(tbody)) == 0:
                        continue
                    
                    trs1 = tbody[0].findAll("tr")
                    if len(trs1) == 1:
                        continue
                    tds1 = trs1[1].findAll("td")
                    if len(tds1) == 0:
                        continue
                    
                    #print(tds[3].text)
                    
        
                    f_pcr.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds1[1].text.replace(",","")+","+tds1[2].text.replace(",","")+","+tds1[3].text.replace(",","")+","+tds1[4].text.replace(",","")+","+tds1[5].text.replace(",","")+","+tds1[6].text.replace(",","")+",\n")
                except:
                    looptime = 0
                    while looptime < 10:
                        print ("except!!! no OK")
                        r = requests.get("http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=" + str(yr) + "/" + str(mon) + "/" + str(day) + "&dateend=" + str(yr) + "/" + str(mon) + "/" + str(day), auth=('user', 'pass'))
                        #print("http://www.taifex.com.tw/chinese/3/PCRatio_tbl.asp?datestart=" + str(yr) + "/" + str(mon) + "/" + str(day) + "&dateend=" + str(yr) + "/" + str(mon) + "/" + str(day))
                        r.encoding = "utf-8"
                        if "日期：" in r.text:
                            htmly,htmlm,htmld = r.text.split("日期：")[1].split("</h3>")[0].split("/")[0],r.text.split("日期：")[1].split("</h3>")[0].split("/")[1],r.text.split("日期：")[1].split("</h3>")[0].split("/")[2]
                            if int(htmly) != yr or int(htmlm) != mon or int(htmld) != day:
                                print(yr,mon,day)
                                time.sleep(3)
                                continue
                        soup = bs(r.text)
                        
                        tbody = soup.findAll("table", {"class":"table_a"})
                        
                        if (len(tbody)) == 0:
                            continue
                        trs1 = tbody[0].findAll("tr")
                        if len(trs1) == 1:
                            continue
                        print(trs1)
                        tds1 = trs1[1].findAll("td")
                        if len(tds1) == 0:
                            continue
                        #print(tds[3].text)
                        
            
                        f_pcr.write(str(yr)+"/"+str(mon)+"/"+str(day)+","+tds1[1].text.replace(",","")+","+tds1[2].text.replace(",","")+","+tds1[3].text.replace(",","")+","+tds1[4].text.replace(",","")+","+tds1[5].text.replace(",","")+","+tds1[6].text.replace(",","")+",\n")
                        time.sleep(5+looptime)
                        looptime = looptime + 1
                time.sleep(1)
    f_pcr.close()

#希望新增一個指令是檢查data有沒有問題
#1. data日期重複
#2. data跳太多

if __name__ == '__main__':    
    #while True:
    if True:
        #設定每天下午4點更新
        #if (time.localtime(time.time()).tm_hour >= 16 and time.localtime(time.time()).tm_hour <= 18) or (time.localtime(time.time()).tm_hour == 4):
        if True:
            #print(time.localtime(time.time()).tm_hour, ":", time.localtime(time.time()).tm_min)            
            #更新股票代碼
            #update_list()
            ##更新台指期
            #update_credit()
            update_txf(False)
            update_pcr()
            ##更新權值股
            update_power_list()                        
            #
            ##讀取股票代碼
            stock_list, oct_list = kinfo.load_list()
            #
            ##選擇是否全更新            
            for num in stock_list:
                update_stock(num, False,False)
                if datetime.date.today().weekday() == 5 or datetime.date.today().weekday() == 6:
                    get_adj_close(num)
            #    
            for num in oct_list:
                update_stock(num, True,False)
                if datetime.date.today().weekday() == 5 or datetime.date.today().weekday() == 6:
                    get_adj_close(num)
        else:
            print(time.localtime(time.time()).tm_hour, ":", time.localtime(time.time()).tm_min)
            time.sleep(30*60)
    
        
    