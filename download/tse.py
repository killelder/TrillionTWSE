# -*- coding:utf-8 -*-

#http://www.twse.com.tw/zh/ 首頁

import yaml
import os
import requests
from bs4 import BeautifulSoup as bs    
import time
import codecs
import pandas as pd

dirpath = os.path.join(os.path.dirname(__file__), "../../data/")
sleeptime = 3

def dictsortkeys(a):
    ''' dict to list '''
    keys = a.keys()
    vals = []
    
    for buf in keys:
        vals.append(buf)
        
    vals.sort()
    print(vals)
    return vals

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
                if len(tds) < 4:
                    continue
                powerdict[int(tds[0].text)] = [tds[1].text,tds[2].text,tds[3].text]
                if len(tds) < 8:
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
        
    def download(self):
        pass
        
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
    
    