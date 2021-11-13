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


class OptionTest(unittest.TestCase):
    def test_GetOptionChain(self):
        getOptionChain()


    def test_NiftyOptions(self):
        Path(OptionsConstants.Location+"\\"+OptionsConstants.TradeDate).mkdir(parents=True, exist_ok=True)
        print(OptionsConstants.Location+"\\"+OptionsConstants.TradeDate)
        CreateCallAndPutData('C:\\Users\\srepswal\\Desktop\\test.json')
        callList=CreateExpectedSpotLists("call")
        putList=CreateExpectedSpotLists("put")
        CalculateLossAndProfit(callList, putList)

    def test_MapNiftyOptions(self):

        df1=MappingForZerodha("call")
        df2 = MappingForZerodha("put")
        resultdf=pd.merge(df1,df2)
        tradeObject = Trade()
        tradeObject.launchSite("https://kite.zerodha.com")
        tradeObject.loginToApp("le9907", "Sr284080399", "298711")
        time.sleep(1)


        tradeObject.NavigateToWatchList("3")
        time.sleep(3)
        tradeObject.clearWatchList()

        time.sleep(1)

        # print(data.iloc[:,1])
        symbolSet=dict()
        for index, row in resultdf.iterrows():
            if(row["callSymbol"] not in symbolSet):
                callSymbol=tradeObject.SearchAddOptionSymbol(row["callSymbol"])
                symbolSet[row["callSymbol"]]=callSymbol
            resultdf['callSymbol'][index] = symbolSet[row["callSymbol"]]

        time.sleep(1)

        tradeObject.NavigateToWatchList("4")
        time.sleep(1)
        tradeObject.clearWatchList()
        time.sleep(1)
        for index, row in resultdf.iterrows():
            if (row["putSymbol"] not in symbolSet):
                putSymbol = tradeObject.SearchAddOptionSymbol(row["putSymbol"])
                symbolSet[row["putSymbol"]]=putSymbol
            resultdf['putSymbol'][index] = symbolSet[row["putSymbol"]]
        tradeObject.driver.quit()
        with pd.ExcelWriter(
                OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx",
                engine="xlsxwriter") as writer:
            resultdf.to_excel(writer, index=False)

    def test_getOptionPrices(self):
        tradeObject = Trade()
        tradeObject.launchSite("https://kite.zerodha.com")
        tradeObject.loginToApp("le9907", "Sr284080399", "298711")
        time.sleep(3)

        tradeObject.NavigateToWatchList("3")
        time.sleep(3)
        source = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx"
        OriginalData = pd.read_excel(source)
        callData = pd.read_excel(source, usecols=['callSymbol']).drop_duplicates()
        callData=tradeObject.getOptionPrices(callData,"call",OptionsConstants.PriceSuffix)
        OriginalData =pd.merge(OriginalData,callData)

        tradeObject.NavigateToWatchList("4")
        time.sleep(4)
        putData = pd.read_excel(source, usecols=['putSymbol']).drop_duplicates()
        putData = tradeObject.getOptionPrices(putData, "put", OptionsConstants.PriceSuffix)
        resultdf = pd.merge(OriginalData, putData)
        if ('Buy' in (OptionsConstants.PriceSuffix.capitalize())):
            resultdf = getChangeInPrice(resultdf, "Call", "call_" + OptionsConstants.PriceSuffix)
        tradeObject.driver.quit()
        with pd.ExcelWriter(
                # OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_15_"+OptionsConstants.FileSuffix+".xlsx",
                OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_" + OptionsConstants.PriceSuffix + ".xlsx",
                engine="xlsxwriter") as writer:
            resultdf.to_excel(writer, index=False)

    def test_getParams(self):

        source = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_" + OptionsConstants.PriceSuffix + ".xlsx"
        OriginalData = pd.read_excel(source)
        resultdf= OriginalData.sort_values(['Call_Change','Put_Change'],ascending=[True, False])
        resultdf['Call_ITM']="N"
        resultdf['Put_ITM'] = "N"
        resultdf["currExpiry"] = "N"
        for index, row in resultdf.iterrows():
            callStrike = (int)(row[ 'call_Strike'])
            putStrike = (int)(row['put_Strike'])
            if(callStrike<OptionsConstants.CurrSpot):
                resultdf['Call_ITM'][index] = "Y"
            if (putStrike > OptionsConstants.CurrSpot):
                resultdf['Put_ITM'][index] = "Y"

            callExpiry = (datetime.datetime.strptime(row['call_Expiry'], '%d-%b-%Y'))
            putExpiry = (datetime.datetime.strptime(row['put_Expiry'], '%d-%b-%Y'))
            dt_call = callExpiry + relativedelta(day=7, weekday=TH(-1))
            dt_put = putExpiry + relativedelta(day=7, weekday=TH(-1))
            if(callExpiry==dt_call or putExpiry==dt_put ):
                resultdf["currExpiry"][index]="Y"

        with pd.ExcelWriter(
                # OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_15_"+OptionsConstants.FileSuffix+".xlsx",
                OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_" + OptionsConstants.PriceSuffix + ".xlsx",
                engine="xlsxwriter") as writer:
            resultdf.to_excel(writer, index=False)

    def test_getPricesFromFile(self):
        source = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx"
        callList = pd.read_excel(source)
        callList_updated= CreateOptionData('C:\\Users\\srepswal\\Desktop\\test.json','CE')
        callList=pd.merge(callList,callList_updated[['expiryDate','strikePrice','lastPrice']],left_on =['call_Expiry','call_Strike'], right_on =['expiryDate','strikePrice'],how='left')
        callList=callList.drop(columns={'expiryDate','strikePrice'})
        callList=callList.rename(columns={"lastPrice":'call_'+OptionsConstants.PriceSuffix})

        putListt_updated = CreateOptionData('C:\\Users\\srepswal\\Desktop\\test.json', 'PE')
        callList = pd.merge(callList, putListt_updated[['expiryDate', 'strikePrice', 'lastPrice']],
                            left_on=['put_Expiry', 'put_Strike'], right_on=['expiryDate', 'strikePrice'], how='left')
        callList = callList.drop(columns={'expiryDate', 'strikePrice'})
        callList = callList.rename(columns={"lastPrice": 'put_' + OptionsConstants.PriceSuffix})

        with pd.ExcelWriter(
                # OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_15_"+OptionsConstants.FileSuffix+".xlsx",
                OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_" + OptionsConstants.PriceSuffix + ".xlsx",
                engine="xlsxwriter") as writer:
            callList.to_excel(writer, index=False)

    def test_createSymbolList(self):
        filepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\IndexSymbols.txt"
        try:
            os.makedirs(OptionsConstants.Location + "\\" + OptionsConstants.TradeDate)
        except OSError:
            pass

        for currSymbol in OptionsConstants.SymbolList:
            with open(filepath, 'a') as outfile:
                outfile.write(currSymbol+'\n')
    # Get All the option params for defined index options list
    def test_GetOptionList(self):
        filepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\IndexSymbols.txt"
        ActiveIndexfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\ActiveIndexSymbols.txt"
        ActiveSymbols=""
        output=""
        with open(filepath, 'r') as f:
                for currSymbol in f:
                    try:
                        getOptionChain(currSymbol.replace('\n',""))
                        ActiveSymbols = ActiveSymbols + currSymbol
                        time.sleep(10)
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



    def test_getPrices(self):
        ActiveIndexfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\ActiveIndexSymbols.txt"
        with open(ActiveIndexfilepath, 'r') as f:
                for currSymbol in f:
                    currSymbol=currSymbol.replace('\n',"")
                    getOptionChain(currSymbol.replace('\n', ""))
                    getPricesFromFile(currSymbol=currSymbol)


    def test_Adhoc(self):
        currSymbol="NIFTY"
        # currSymbol = "Sheet1"
        callList = CreateSpotListsWithGreeks("call", currSymbol)
        putList = CreateSpotListsWithGreeks("put", currSymbol)
        GetOptionGreekCombination(callList, putList, currSymbol)
        filepath =OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionGreek_Add"+OptionsConstants.FileSuffix+".xlsx"
        GetOptionGreekCombination(callList, putList, currSymbol,"+",filepath)