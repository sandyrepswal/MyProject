import pandas
from openpyxl import load_workbook
from selenium.webdriver import ActionChains

from Main.DriverObject import SeleniumDriver as SD
from win32com.client import Dispatch
from datetime import datetime
import time
import pandas as pd
import xlsxwriter
class Trade:
    currDate=datetime.today().strftime('%Y%m%d')

    def __init__(self):
        self.driver = None
    def launchSite(self,url):
        self.driver=SD.SeleniumDriver.launchWebsite("Chrome",url)
        # input("Press Enter to continue...")

    def loginToApp(self,username,password,passkey):
        self.driver.find_element_by_css_selector("input#userid").send_keys(username)
        self.driver.find_element_by_css_selector("input#password").send_keys(password)
        self.driver.find_element_by_css_selector("button[type='submit']").click();
        time.sleep(2)
        self.driver.find_element_by_css_selector("input#pin").send_keys(passkey)
        self.driver.find_element_by_css_selector("button[type='submit']").click();

    def NavigateToWatchList(self,number):
        watchListLocator="li[data-balloon*='index']"
        self.driver.find_element_by_css_selector(watchListLocator.replace("index",number)).click()

    def SearchAndAddSecurity(self,searchString):
        self.driver.find_element_by_css_selector("input#search-input").send_keys(searchString)
        time.sleep(.5)
        # self.driver.find_element_by_css_selector("ul.search-result-list li").click()
        self.driver.find_element_by_css_selector("ul.search-result-list li span.symbol").click()

    def SearchAddOptionSymbol(self, searchString):
        self.driver.find_element_by_css_selector("input#search-input").send_keys(searchString)
        time.sleep(.5)
        # self.driver.find_element_by_css_selector("ul.search-result-list li").click()
        SymbolText=self.driver.find_element_by_css_selector("ul.search-result-list li span.symbol").text
        self.driver.find_element_by_css_selector("ul.search-result-list li span.symbol").click()
        return(SymbolText)

    def AddWatchList(self):
        destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
        data = pd.read_excel(destination,sheet_name=Trade.currDate, usecols="A:H")
        # print(data.iloc[:,1])
        for currSec in data.iloc[:, 0]:
            self.SearchAndAddSecurity(currSec)


    def clearWatchList(self):
        try:
            result=True
            while(result):
                currSec=self.driver.find_element_by_css_selector("div[class*='vddl-draggable instrument']")
                hover = ActionChains(self.driver).move_to_element(currSec)
                hover.perform()
                currSec.find_element_by_css_selector("span[data-balloon*='Delete'] button").click()
                time.sleep(.5)
            print()
        except Exception as inst:
            print(type(inst))
            time.sleep(1)


    def getDepthDetails(self,data,currRow,currSec):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", currSec)
            hover = ActionChains(self.driver).move_to_element(currSec).click()
            hover.perform()

            currSec.find_element_by_css_selector("span[data-balloon='Market Depth (D)'] button").click()
            time.sleep(.5)
            Open=currSec.find_element_by_xpath("//label[text()='Open']/following-sibling::span").text
            data["Open"][currRow] = Open
            High = currSec.find_element_by_xpath("//label[text()='High']/following-sibling::span").text
            data["High"][currRow] = High
            Low = currSec.find_element_by_xpath("//label[text()='Low']/following-sibling::span").text
            data["Low"][currRow] = Low
            Avg_Price = currSec.find_element_by_xpath("//label[text()='Avg. price']/following-sibling::span").text
            data["Avg_Price"][currRow] = Avg_Price
            Volume = currSec.find_element_by_xpath("//label[text()='Volume']/following-sibling::span").text
            data["Volume"][currRow] = Volume
            LTQ = currSec.find_element_by_xpath("//label[text()='LTQ']/following-sibling::span").text
            data["LTQ"][currRow] = LTQ
            hover = ActionChains(self.driver).move_to_element(currSec)
            hover.perform()
            currSec.find_element_by_css_selector("span[data-balloon='Market Depth (D)'] button").click()
            time.sleep(.2)
        except Exception as inst:
            print(type(inst))
            time.sleep(1)


    def getSecurityDetails(self):
        destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
        data = pd.read_excel(destination, sheet_name=Trade.currDate, usecols="A:H")
        data.fillna(0)

        data["Change"] = 0
        data["Price"] = 0
        data["Open"] = 0
        data["High"] = 0
        data["Low"] = 0
        data["Avg_Price"] = 0
        data["Volume"] = 0
        data["LTQ"] = 0
        data.fillna(0)
        # data["Change"] = data["Change"].fillna('')
        # data["Price"] = data["Price"].fillna('')
        # data["Open"] = data["Open"].fillna('')
        # data["High"] = data["High"].fillna('')
        # data["Low"] = data["Low"].fillna('')
        # data["Avg_Price"] = data["Avg_Price"].fillna('')
        # data["Volume"] = data["Volume"].fillna('')
        # data["LTQ"] = data["LTQ"].fillna('')

        listOfsecurity = self.driver.find_elements_by_css_selector("div[class*='vddl-draggable instrument']")
        time.sleep(2)
        for currSec in listOfsecurity:
            Name = currSec.find_element_by_css_selector("span[class='nice-name']").text
            currRow=data.iloc[:,0].str.contains(Name)
            Change = currSec.find_element_by_css_selector("span[class='dim']").text
            data["Change"][currRow] = Change
            Price = currSec.find_element_by_css_selector("span[class='last-price']").text
            data["Price"][currRow] = Price
            self.getDepthDetails(data,currRow,currSec)
        book = load_workbook(destination)
        writer = pandas.ExcelWriter(destination, engine='openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        data.to_excel(writer, sheet_name=Trade.currDate, index=False)
        writer.save()
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        #     data.to_excel(writer, sheet_name=Trade.currDate,index=False)

    def getOptionPrices(self,data,OptionType,PriceType):
        data[OptionType+"_"+PriceType] = 0.0
        for index, row in data.iterrows():
            try:
                currSecElem=  self.driver.find_element_by_xpath("//*[.='"+row[OptionType+"Symbol"]+"']//ancestor::div[contains(@class,'vddl-draggable instrument')]")
                self.driver.execute_script("arguments[0].scrollIntoView();", currSecElem)
                time.sleep(.5)
                data[OptionType + "_" + PriceType][index] =float(currSecElem.find_element_by_css_selector("span[class='last-price']").text)
                time.sleep(.5)
            except Exception as inst:
                print(type(inst))
                time.sleep(1)
        return(data)




    def tradesToExecute(self,positionSize,quantity,SlMarginPercent=.25):
        #open excel
        ExcelRecords=[]
        for currRecords in ExcelRecords:
            change=10 #get from excel record
            price=10 #get from excel record
            if change>0.5:
                marginReq= price*quantity
                if(positionSize-marginReq>1000):
                    side="buy"
                    tradeSL=(price*SlMarginPercent/100+price)
                else:
                    side="No Margin"
            elif (change<-0.5):
                marginReq = price * quantity
                if (positionSize - marginReq > 1000):
                    side = "sell"
                    tradeSL = (price-price * SlMarginPercent/100 )
                else:
                    side = "No Margin"
            else:
                side="not enough clarity"
        #close excel

    def copyToDataExcel(self,source,destination):
       # data = pd.read_excel(source, sheet_name="Sheet1",usecols="A:H")
        data = pd.read_excel(source, sheet_name="Sheet1")

        # save it to the 'new_tab' in destfile
        with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
            data.to_excel(writer, sheet_name=Trade.currDate,index=False)

