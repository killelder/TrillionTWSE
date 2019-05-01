# -*- coding:utf-8 -*-

#http://www.twse.com.tw/zh/ 首頁

import yaml
import os
import requests
from bs4 import BeautifulSoup as bs    
import time
import codecs
import pandas as pd
import json
dirpath = os.path.join(os.path.dirname(__file__), "../../data/")
sleeptime = 3

def dictsortkeys(a):
    """ 
        dict to list 
    """
    keys = a.keys()
    vals = []
    
    for buf in keys:
        vals.append(buf)
        
    vals.sort()
    print(vals)
    return vals

def check_last_date(number):
    """
        檢查data檔案內的最後更新日期
    """
    if os.path.exists(dirpath + "Price/" + str(number) + ".csv") == False:
        return 1992, 0, 0
    f = open(dirpath + "Price/" + str(number) + ".csv", "r")
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

class misc_information():
    """
        other information
        1. download stock list complete
        2. download power list complete
        3. download 申購 list
    """
    def __init__(self):
        self.stocklistpath = "stocklist.csv"   #存股票list位置
        self.warrantlistpath = "warrant.csv"   #存權證list位置
        self.powerlistpath = "powerstock.csv"  #存權值股list位置
        self.purchaselistpath = "perchase.csv" #申購股list位置
        self.stocklisturl = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"    #上市股票代碼表
        self.otclisturl = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4"    #上櫃股票代碼表
        self.powerlisturl = "http://www.taifex.com.tw/cht/2/weightedPropertion"         #權值股代碼表
        self.purchaselisturl = "https://www.wantgoo.com/stock/twstock/draw"    #申購表
        
    def download_stock_list(self):    
        """
            更新股票list
            一天只會download一次
            download下來是big5
        """
        if os.path.exists(dirpath + self.stocklistpath) == True:
            file_t = time.localtime(os.path.getmtime(dirpath + self.stocklistpath))
            local_t = time.localtime(time.time())
            if time.strftime("%Y%m%d",file_t) == time.strftime("%Y%m%d",local_t):
                print("Today already update stock number list.")
                return 1
        
        #更新上市代碼    
        #no_res = requests.get(self.stocklisturl, auth=("user", "pass"))
        no_res = requests.get(self.stocklisturl)#, auth=("user", "pass"))
        
        soup = bs(no_res.text)
        trs = soup.findAll("tr")
        f_stock = codecs.open(dirpath + self.stocklistpath, "w", "big5", "ignore")
        f_stock.write("代號,股票名稱,上市櫃,產業別,\n")
        
        f_warrant = codecs.open(dirpath + self.warrantlistpath, "w", "big5", "ignore")
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
        no_res = requests.get(self.otclisturl)#, auth=("user", "pass"))
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

    def download_power_list(self):
        """
            更新權值股
            一天更新一次
        """
        if os.path.exists(dirpath + self.powerlistpath) == True:
            file_t = time.localtime(os.path.getmtime(dirpath + self.powerlistpath))
            local_t = time.localtime(time.time())
            if time.strftime("%Y%m%d",file_t) == time.strftime("%Y%m%d",local_t):
                print("Today already update power stock number list.")
                return 1
        
        no_res = requests.get(self.powerlisturl)#, auth=("user", "pass"))
        no_res.encoding = "utf-8"
        soup = bs(no_res.text)
        divs = soup.findAll("div", {"id":"printhere"})        
        powerdict = dict()
        for buf in divs:
            trs = buf.findAll("tr")
           
            for buf2 in trs:
                tds = buf2.findAll("td")
                #print(len(tds))
                if len(tds) < 4:
                    continue
                powerdict[int(tds[0].text)] = [tds[1].text,tds[2].text,tds[3].text]
                if len(tds) < 8:
                    continue
                #print(tds[4].text)
                if "\n" in tds[4].text:
                    continue
                powerdict[int(tds[4].text)] = [tds[5].text,tds[6].text,tds[7].text]
        
        keysort = dictsortkeys(powerdict)
        f_power = codecs.open(dirpath + self.powerlistpath, "w") 
        f_power.write("順序,代號,股票名稱,佔比,\n")
        for buf in keysort:
            f_power.write(str(buf)+","+powerdict[buf][0]+","+powerdict[buf][1]+","+powerdict[buf][2]+",")
            f_power.write("\n")
        f_power.close()
        del(no_res)
        del(soup)
        print("Update stock number list finish.")
        
        return 0
    
    def download_purchase_list(self):    
        """
            更新申購表
            一天只會download一次
        """
        L = Lottery()
        L.download(0)        
        return 0
        
class Stock_daily():
    def __init__(self):
        pass
    
    def load_list(self):
        """
            load stock list
            load otc list
        """
        stock_list = []
        oct_list = []
        f = open(dirpath + "stocklist.csv", "r")
        f.readline()
        for buf in f:
            buf2 = buf.replace("\n","").split(",")
            if "上市" in buf2[2]:
                stock_list.append(int(buf2[0]))
            if "上櫃" in buf2[2]:
                oct_list.append(int(buf2[0]))
        f.close()
        return stock_list, oct_list

    def download(self):
        """
            更新所有股價, 除權息資訊
        """
        stock_list, oct_list = self.load_list()
        for num in stock_list:
            self.download_stock(num, False,False)
            #if datetime.date.today().weekday() == 5 or datetime.date.today().weekday() == 6:
            #    self.download_adj_close(num)
        #    
        for num in oct_list:
            self.download_stock(num, True,False)
            #if datetime.date.today().weekday() == 5 or datetime.date.today().weekday() == 6:
            #    self.download_adj_close(num)

    def download_stock(self, number, isotc, forceupdate=False):
        """
            下載上市櫃股票專用
        """
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
            f = open(dirpath + "Price/" + str(number) + ".csv", "w")
            f.write("time,open,high,low,close,turnover,volume\n")
        else:
            if os.path.exists(dirpath + "Price/" + str(number) + ".csv") == False:
                f = open(dirpath + "Price/" + str(number) + ".csv", "a")
                f.write("time,open,high,low,close,turnover,volume\n")
            else:
                f = open(dirpath + "Price/" + str(number) + ".csv", "a")
        
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
                        r = requests.get("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number))#, auth=('user', 'pass'))
                        print("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number))
                        stockdata = json.loads(r.text)
                        time.sleep(waitt)
                    except:
                        while True:
                            print ("except!!! no OK")
                            time.sleep(delayt)
                            try:
                                r = requests.get("http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + str(year) + monstr + "01" "&stockNo=" + str(number))#, auth=('user', 'pass'))
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
                        r = requests.get("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number))#, auth=('user', 'pass'))
                        print("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number))
                        stockdata = json.loads(r.text)                    
                        time.sleep(waitt)
                    except:
                        while True:
                            print ("except!!! no OK")
                            time.sleep(delayt)
                            try:
                                r = requests.get("http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d=" + str(twyear) + "/" + monstr + "&stkno=" + str(number))#, auth=('user', 'pass'))
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
        
class Lottery():
    def __init__(self):
        pass
    
    def download(self, year, forceupdate=False):
        """
            start from 2006, < 2006 會 download all
            申購網頁 : http://www.tse.com.tw/announcement/publicForm?response=json&yy=2018&_=1544101760642
        """    
        
        if year < 2006:
            this_year = int(time.strftime("%Y", time.gmtime(time.time())))
            print(this_year)
            for year in range(2006, this_year+1):
                if os.path.exists(dirpath + "Lottery/" + str(year) + ".yaml") == True:
                    file_t = time.localtime(os.path.getmtime(dirpath + "Lottery/" + str(year) + ".yaml"))
                    local_t = time.localtime(time.time())
                    if time.strftime("%Y%m",file_t) == time.strftime("%Y%m",local_t):
                        print("Today already update purchase list.")
                        return 1
                res = requests.get("http://www.tse.com.tw/announcement/publicForm?response=json&yy=" + str(year) + "&_=1544101760642")
                soup = bs(res.text)
                msg = soup.findAll("body")[0].text
                buf = yaml.safe_load(msg)
                with open(dirpath + "Lottery/" + str(year) + ".yaml", 'w') as outfile:
                    yaml.dump(buf, outfile, allow_unicode=True)
                time.sleep(sleeptime)
                
        else:
            res = requests.get("http://www.tse.com.tw/announcement/publicForm?response=json&yy=" + str(year) + "&_=1544101760642")
            soup = bs(res.text)
            msg = soup.findAll("body")[0].text
            buf = yaml.safe_load(msg)
            print(buf)
            with open(dirpath + "Lottery/" + str(year) + ".yaml", 'w') as outfile:
                yaml.dump(buf, outfile, allow_unicode=True)
        
        print("Download Lottery complete")
        return 0
        
    def load(self, year):    
        """
            return pandas data with title           
        """
        out_data = dict()
        title = ["序號","抽籤日期","證券名稱","證券代號","發行市場","申購開始日","申購結束日","承銷股數","實際承銷股數","承銷價(元)","實際承銷價(元)","撥券日期(上市、上櫃日期)","主辦券商","申購股數","總承銷金額(元)","總合格件","中籤率(%)","取消公開抽籤"]
        with open(dirpath + "Lottery/" + str(year) + ".yaml", 'r') as stream:
            data = pd.DataFrame(yaml.safe_load(stream)["data"], columns=title)
            
            return data
    
if __name__ == "__main__":
    m = misc_information()
    m.download_purchase_list()
    m.download_power_list()
    m.download_stock_list()
    
    