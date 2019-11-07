from download import tse

if __name__ == "__main__":
    a = tse.misc_information()
    a.download_purchase_list()
    a.download_stock_list()
    a.download_power_list()
    c = tse.Stock_daily()
    #c.changetoADall()
    c.download()
    