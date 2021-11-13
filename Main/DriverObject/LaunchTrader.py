import time
import pandas as pd

from bs4 import BeautifulSoup

from Main.DriverObject import SeleniumDriver as SD


def navigateToScreener(driver):
    driver.find_element_by_link_text("Screener").click()


def navigateToStockScreener(driver):
    navigateToScreener(driver)
    driver.find_element_by_link_text("Stock Screener").click()


def getAllRows(driver):
    listofRows = driver.find_elements_by_tag_name("tr")
    return (listofRows)

def writeSource(driver,path):
    mytext =open(path,"w", encoding="utf-8")
    test= driver.page_source
    test = str(test)
    print(type(test))
    mytext.write(test)
    mytext.close()

def writeFormatted(driver,path):
    mytext =open(path,"w+", encoding="utf-8")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    rows = soup.find_all("tr")
    col_list = []
    row_list=list()
    th=soup.find_all("th")
    for i in th:
        currHead=(i.text).replace("\n","")
        if not(col_list.__contains__(currHead)):
            col_list.append(currHead)
    i=len(col_list)
    col_list.pop(i-1)


    # row = [i.text for i in th]
    # col_list.append(row)
    mytext.writelines(col_list)
    for tr in rows:

        td = tr.find_all("td")
        row = []
        try:
           row.append(tr.get('data-symbol'))
        except Exception as inst:
           type(inst)

        count=0
        print(type(count))
        for i in td:
            if (count!=0):
                row.append(i.text.replace("\n", "").replace("-", ""))
            count=count+1
        if(row.__len__()>1):
            #mytext.writelines(row)
            row_list.append(row)
    mytext.close()

    df_bs = pd.DataFrame(row_list, columns=col_list)
    #df_bs.set_index('TickerNo', inplace=True)
    with pd.ExcelWriter('beautifulsoup.xlsx', engine="openpyxl") as writer:
        df_bs.to_excel(writer,  index=False)
    #df_bs.to_csv('beautifulsoup.xlsx',encoding='utf-8-sig')



#
driver = SD.SeleniumDriver.launchWebsite("Chrome","http://in.tradingview.com")
# driver = SD.SeleniumDriver.launchWebsite("Chrome","C:\\Users\\srepswal\\Downloads\\localStocks.html")

#navigateToScreener(driver)
#rows=getAllRows(driver)
#time.sleep(15)
# writeSource(driver,"test.txt")
writeFormatted(driver,"test1.txt")
driver.quit()




