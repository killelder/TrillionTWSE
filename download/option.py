import os
import requests
from bs4 import BeautifulSoup as bs    
import time
import codecs
import pandas as pd
import json

dirpath = os.path.join(os.path.dirname(__file__), "../../data/")

def dl_opt_daily_price():
    """
        2002 開始有TXO
        2013 開始有周選
        結尾P 是Put
        結尾C 是Call
        結尾PW 是Put Week
        結尾CW 是Call Week
    """
    #http://www.taifex.com.tw/cht/3/optDailyMarketReport?queryType=2&marketCode=0&commodity_id=TXO&queryDate=2019/04/22&MarketCode=0&commodity_idt=TXO
    #給定更新起始年月日
    
    this_year = int(time.strftime("%Y"))+1 #+1是為了for迴圈連今年也要跑
    toyr, tomon, today = time.localtime(time.time()).tm_year, time.localtime(time.time()).tm_mon, time.localtime(time.time()).tm_mday
    waitt = 3
    
    for year in range(2002, this_year):
        for mon in range(1, 13): 
            monstr = ""
            if mon < 10:
                monstr = "0" + str(mon)
            else:
                monstr = str(mon)
            if (year > toyr) or (year == toyr and mon > tomon):
                continue
            print(year, mon)
            for day in range(1, 31):
                if (mon == tomon and day > today):
                    continue
                daystr = ""
                if day < 10:
                    daystr = "0" + str(day)
                else:
                    daystr = str(day)

                if os.path.exists(dirpath + "Option/" + str(year) + monstr + daystr + "C" + ".csv"):
                    continue
                else:
                    rptc = open(dirpath + "Option/" + str(year) + monstr + daystr + "C" + ".csv", "w")
                    rptp = open(dirpath + "Option/" + str(year) + monstr + daystr + "P" + ".csv", "w")
                    rptcw = open(dirpath + "Option/" + str(year) + monstr + daystr + "CW" + ".csv", "w")
                    rptpw = open(dirpath + "Option/" + str(year) + monstr + daystr + "PW" + ".csv", "w")

                    delayt = 1
                    try:
                        r = requests.get("http://www.taifex.com.tw/cht/3/optDailyMarketReport?queryType=2&marketCode=0&commodity_id=TXO&queryDate=" + str(year) + "/" + monstr + "/" + daystr + "&MarketCode=0&commodity_idt=TXO")
                        soup = bs(r.text)
                        tbs = soup.find("table",{"class":"table_f"})
                        trs = tbs.findAll("tr")
                        for buf in trs:
                        	#print(buf)
                        	if "TXO" in buf.text:
                        		print(buf)
                        		#buf2 = buf.findAll("td")
                        		#for buf3 in buf2:


        				#trs = soup.findAll("tr")
                        #stockdata = json.loads(r.text)
                        time.sleep(waitt)
                    except:
                        while True:
                            print ("except!!! no OK")
                            time.sleep(delayt)
                            try:
                                r = requests.get("http://www.taifex.com.tw/cht/3/optDailyMarketReport?queryType=2&marketCode=0&commodity_id=TXO&queryDate=" + str(year) + "/" + monstr + "/" + daystr + "&MarketCode=0&commodity_idt=TXO")
                                #stockdata = json.loads(r.text)
                                break
                            except:
                                delayt = delayt + 1
                            finally:
                                if delayt >= 11:
                                    break
                    finally:
                        pass
                        #"0日期","1成交股數","2成交金額","3開盤價","4最高價","5最低價","6收盤價","7漲跌價差","8成交筆數"
                        #if "OK" == stockdata["stat"]:
                        #    for i in range(0, len(stockdata["data"])):
                        #        if year <= yearstart and mon <= monstart and int(stockdata["data"][i][0].split("/")[2]) <= daystart:
                        #            continue
                        #        f.write(stockdata["data"][i][0].replace(",","") + "," + stockdata["data"][i][3].replace(",","") + "," + stockdata["data"][i][4].replace(",","") + "," + stockdata["data"][i][5].replace(",","") + "," + stockdata["data"][i][6].replace(",","") + "," + stockdata["data"][i][8].replace(",","")  + "," + stockdata["data"][i][1].replace(",","") + "\n")
                        #else:
                        #    print ("ERROR no OK")

if __name__ == "__main__":
    dl_opt_daily_price()
    pass