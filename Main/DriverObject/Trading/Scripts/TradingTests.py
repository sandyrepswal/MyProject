import datetime
import unittest
import time
import pandas as pd
from Main.DriverObject.Trading.Scripts.Trade import Trade


class MyTestCase(unittest.TestCase):
    def test_clearWatchList(self):
        tradeObject=Trade()
        tradeObject.launchSite("https://kite.zerodha.com")
        tradeObject.loginToApp("le9907","Sr284080399","298711")
        time.sleep(2)
        tradeObject.NavigateToWatchList("2")
        tradeObject.clearWatchList()
        tradeObject.driver.quit()

    def test_AddWatchList(self):
        tradeObject=Trade()
        tradeObject.launchSite("https://kite.zerodha.com")
        tradeObject.loginToApp("le9907","Sr284080399","298711")
        time.sleep(2)
        tradeObject.NavigateToWatchList("2")
        tradeObject.AddWatchList()
        tradeObject.driver.quit()


    def test_copyToTradeData(self):
        T = Trade()
        source = 'C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\beautifulsoup.xlsx'
        destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
        T.copyToDataExcel(source, destination)

    def test_getAllSecurity(self):
        destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
        data = pd.read_excel(destination,  usecols="A:H")
        # print(data.iloc[:,1])
        for currSec in data.iloc[:,0]:
            print(currSec)

    def test_RemoveIlliquidSecurity(self):
        destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
        xls = pd.ExcelFile(destination)
        data = pd.read_excel(xls,sheet_name="20210112")
        Liquid = pd.read_excel(xls, sheet_name="MIS")
        print(data.loc['A':])
        print(data.loc['A':] .isin(data.loc['A':]))


    def test_getSecurityDetails(self):
        tradeObject=Trade()
        tradeObject.launchSite("https://kite.zerodha.com")
        tradeObject.loginToApp("le9907","Sr284080399","298711")
        time.sleep(2)
        tradeObject.NavigateToWatchList("2")
        tradeObject.getSecurityDetails()