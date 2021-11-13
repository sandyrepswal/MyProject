import calendar
import datetime
import time
import unittest
import json
import requests
import pandas as pd
from pathlib import Path

from dateutil.relativedelta import relativedelta, TH
from pyblackscholesanalytics.market.market import MarketEnvironment
from Main.DriverObject.Trading.Scripts.OptionScripts import *
from Main.DriverObject.Trading.Scripts.Trade import Trade


class MyTestCase(unittest.TestCase):
    StockSymbol='DRREDDY'

    def test_GetActiveStockOptions(self):
        getTopSecurities()

    def test_createStockSymbolList(self):
        filepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\StockSymbols.txt"
        JsonPath="C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\ActiveStocks.json"
        try:
            os.makedirs(OptionsConstants.Location + "\\" + OptionsConstants.TradeDate)
        except OSError:
            pass

        with open(JsonPath) as f:
            data = json.load(f)
        df = pd.DataFrame(list(data["data"][0:]), columns=['underlying']).drop_duplicates()
        # df = pd.DataFrame(df['underlying'].values.tolist())
        with open(filepath, 'a') as outfile:
            for index, row in df.iterrows():
                outfile.write(row['underlying']+"\n")

    # Get All the option params for defined index options list
    def test_GetOptionList(self):
        filepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\StockSymbols.txt"
        ActiveIndexfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\ActiveStockSymbols.txt"
        ActiveSymbols=""
        output=""
        with open(filepath, 'r') as f:
                for currSymbol in f:
                    try:
                        getOptionChain(currSymbol.replace('\n',""),testurl = "https://www.nseindia.com/api/option-chain-equities?symbol=")
                        ActiveSymbols = ActiveSymbols + currSymbol
                        time.sleep(60)
                        currSymbol = currSymbol.replace('\n', "")
                        currSymbolfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\" + currSymbol + ".json"
                        CreateCallAndPutData(currSymbolfilepath, currSymbol.replace('\n', ""))
                        callList = CreateExpectedSpotLists("call", currSymbol)
                        putList = CreateExpectedSpotLists("put", currSymbol)
                        CalculateLossAndProfit(callList, putList, currSymbol)
                    except:
                        output=output+currSymbol
        with open(filepath, 'w') as outfile:
            outfile.write(output)
        if(ActiveSymbols!=""):
            with open(ActiveIndexfilepath, 'a') as outfile:
                outfile.write(ActiveSymbols)

        # with open(ActiveIndexfilepath, 'r') as f:
        #         for currSymbol in f:
        #             currSymbol=currSymbol.replace('\n',"")
        #             currSymbolfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\" + currSymbol + ".json"
        #             CreateCallAndPutData(currSymbolfilepath,currSymbol.replace('\n',""))
        #             callList = CreateExpectedSpotLists("call",currSymbol)
        #             putList = CreateExpectedSpotLists("put",currSymbol)
        #             CalculateLossAndProfit(callList, putList,currSymbol)


    def test_getPrices(self):
        ActiveIndexfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\ActiveStockSymbols.txt"
        with open(ActiveIndexfilepath, 'r') as f:
                for currSymbol in f:
                    currSymbol=currSymbol.replace('\n',"")
                    getOptionChainForStocks(currSymbol.replace('\n', ""),testurl = "https://www.nseindia.com/api/option-chain-equities?symbol=")
                    getPricesFromFile(currSymbol=currSymbol)
                    time.sleep(40)