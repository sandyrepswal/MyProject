import pandas
import datetime
import os
import time
import unittest
import json
import urllib

import requests
import pandas as pd
from dateutil.relativedelta import relativedelta, TH
from openpyxl import load_workbook
from pyblackscholesanalytics.market.market import MarketEnvironment
import numpy as np
import pandas as pd
import warnings

from pyblackscholesanalytics.market.market import MarketEnvironment
from pyblackscholesanalytics.options.options import PlainVanillaOption, DigitalOption
from sympy import Abs

from Main.DriverObject.Trading.Scripts.OptionConstants import OptionsConstants
from Main.DriverObject.Trading.Scripts.Trade import Trade


def option_factory(mkt_env, plain_or_digital, option_type,K,T):
    option_dispatcher = {
        "plain_vanilla": {"call":   PlainVanillaOption(mkt_env, option_type='call', K=K, T=T),
                          "put": PlainVanillaOption(mkt_env, option_type='put', K=K, T=T)
                          },
        "digital": {"call": DigitalOption(mkt_env),
                    "put": DigitalOption(mkt_env, option_type="put")
                    }
    }

    return option_dispatcher[plain_or_digital][option_type]

def CalcualtePricesForRange(S,option,change=10):
    # print("for currentspot price:", S)
    # print("option price is:", option.price())

    S_min = (int)(S-(S*1.5/100))
    S_max= (int)(S+(S*1.5/100))
    returnList=[]
    for i in range(S_min ,S_max,change) :
        # print("for spot price:",i)
        # print("option price is:",option.price(i))
        OptionPrice= option.price(i)[0]
        returnList.append({'Projected_Spot':i,'Projected_Price':OptionPrice})
    return  returnList

def CalculateMaxLossAndMinProfit(callList,putList):
    resultList=[]
    for i in callList:

        for j in putList:
            maxLoss = 0
            minProfit = 100000
            minProfit_Spot= 1000
            maxLoss_Spot=1000

            callCost=  i['LastPrice']*75 +40
            putCost =  j['LastPrice']*75 +40
            TotalCost =callCost+putCost
            l=0
            for k in i['ProjectedSpot']:
                NewcallCost = k['Projected_Price'] * 75
                NewputCost = j['ProjectedSpot'][l]['Projected_Price'] * 75
                # print(j['Projected_Spot'],j['Projected_Price'])
                l=l+1
                NewTotalCost = NewcallCost+NewputCost;
                currPnL = NewTotalCost-TotalCost
                if(currPnL>0) :
                    if(currPnL<minProfit):
                        minProfit=currPnL
                        minProfit_Spot =  k['Projected_Spot']
                else:
                    if (currPnL < maxLoss):
                        maxLoss=currPnL
                        maxLoss_Spot= k['Projected_Spot']
            resultList.append({'call_Expiry':i['ExpiryDate'],
                               'call_Strike':i['StrikePrice'],
                               'callCost':callCost,
                               'CallPrice':i['LastPrice'],
                               'put_Expiry':j['ExpiryDate'],
                               'put_Strike':j['StrikePrice'],
                               'putCost': putCost,
                               'PutPrice': j['LastPrice'],
                               'totalCost':TotalCost,
                               'minProfit_Spot':minProfit_Spot,
                               'minProfit':minProfit,
                               'maxLoss_Spot':maxLoss_Spot,
                               'maxLoss':maxLoss
                               })
    resultdf = pd.DataFrame(resultList).dropna()
    with pd.ExcelWriter(
            "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx",
            engine="xlsxwriter") as writer:
        resultdf.to_excel(writer, index=False)

def CalculateLossAndProfit(callList,putList,currSymbol="Sheet1"):
    resultList=[]
    for i in callList:
        currStrike = i['StrikePrice']
        S = i['Underlying']
        S_min = (int)(S - (S *2 / 100))
        S_max = (int)(S + (S * 2 / 100))
        if(currStrike<S_min or currStrike>S_max):
        # if (currStrike < S_min):
            continue;
        for j in putList:
            currStrike = j['StrikePrice']
            S_min = (int)(S - (S * 2 / 100))
            S_max = (int)(S + (S * 2 / 100))
            if (currStrike < S_min or currStrike > S_max):
            # if ( currStrike > S_max):
                continue;
            maxLoss = 0
            minProfit = 100000
            minProfit_Spot= 1000
            maxLoss_Spot=1000
            minProfit_Scenario='Neutral'
            maxLoss_Scenario='Neutral'

            callCost=  i['LastPrice']*75 +40
            putCost =  j['LastPrice']*75 +40
            TotalCost =callCost+putCost
            l=0
            for k in i['ProjectedSpot']:
                NewcallCost = k['Projected_Price'] * 75
                NewputCost = j['ProjectedSpot'][l]['Projected_Price'] * 75
                # print(j['Projected_Spot'],j['Projected_Price'])
                l=l+1
                NewTotalCost = NewcallCost+NewputCost;
                currPnL = NewTotalCost-TotalCost
                if(currPnL>0) :
                    if(currPnL<minProfit):
                        minProfit=currPnL
                        minProfit_Spot =  k['Projected_Spot']
                        minProfit_Scenario = "Nifty_Up"
                        if(minProfit_Spot<S):
                            minProfit_Scenario="Nifty_Down"

                else:
                    if (currPnL < maxLoss):
                        maxLoss=currPnL
                        maxLoss_Spot= k['Projected_Spot']
                        maxLoss_Scenario = "Nifty_Up"
                        if (maxLoss_Spot < S):
                            maxLoss_Scenario = "Nifty_Down"
            resultList.append({'call_Expiry':i['ExpiryDate'],
                               'call_Strike':i['StrikePrice'],
                               'callCost':callCost,
                               'CallPrice':i['LastPrice'],
                               'put_Expiry':j['ExpiryDate'],
                               'put_Strike':j['StrikePrice'],
                               'putCost': putCost,
                               'PutPrice': j['LastPrice'],
                               'totalCost':TotalCost,
                               'minProfit_Spot':minProfit_Spot,
                               'minProfit':minProfit,
                               'maxLoss_Spot':maxLoss_Spot,
                               'maxLoss':maxLoss,
                               'minProfit_Scenario':minProfit_Scenario,
                               'maxLoss_Scenario':maxLoss_Scenario
                               })
    resultdf = pd.DataFrame(resultList).dropna()
    filemode = 'w'
    if (os.path.exists(OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx")):
        filemode = 'a'
    with pd.ExcelWriter(
            OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx",
            engine="openpyxl",mode=filemode) as writer:
        resultdf.to_excel(writer,sheet_name=currSymbol, index=False)

def CreateCallAndPutData(JsonPath):
    with open(JsonPath) as f:
        data = json.load(f)
    df = pd.DataFrame(list(data["records"]["data"][0:]), columns=['PE', 'CE']).dropna()

    df2 = pd.DataFrame(df['PE'].values.tolist())
    df2 = df2[(df2['openInterest'] > OptionsConstants.MinOpenInterest) & (df2['impliedVolatility'] > 0) & (df2['totalTradedVolume'] > OptionsConstants.MinTradeVolume)]

    df3 = pd.DataFrame(df['CE'].values.tolist())
    df3 = df3[(df3['openInterest'] > OptionsConstants.MinOpenInterest) & (df3['impliedVolatility'] > 0) & (df3['totalTradedVolume'] > OptionsConstants.MinTradeVolume)]
    # print(data["records"]["data"][0]["PE"]["openInterest"])
    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\put_"+OptionsConstants.FileSuffix+".xlsx",
            engine='xlsxwriter') as writer:
        df2.to_excel(writer, index=False)
    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\call_"+OptionsConstants.FileSuffix+".xlsx",
            engine='xlsxwriter') as writer:
        df3.to_excel(writer, index=False)

# latest 05/02/2021
def CreateCallAndPutData(JsonPath,currSymbol):
    with open(JsonPath) as f:
        data = json.load(f)
    df = pd.DataFrame(list(data["records"]["data"][0:]), columns=['PE', 'CE']).dropna()

    df2 = pd.DataFrame(df['PE'].values.tolist())
    OIMean= df2['openInterest'].mean()
    VolumneMean=df2['totalTradedVolume'].mean()
    df2 = df2[(df2['openInterest'] >=OIMean) & (df2['impliedVolatility'] > 0) & (df2['totalTradedVolume'] > VolumneMean)]
    # df2 = df2[(df2['impliedVolatility'] > 0)]
    # df2 = df2[(df2['openInterest'] > OptionsConstants.MinOpenInterest) & (df2['impliedVolatility'] > 0) & (df2['totalTradedVolume'] > OptionsConstants.MinTradeVolume)]

    df3 = pd.DataFrame(df['CE'].values.tolist())
    # df3 = df3[(df3['openInterest'] > OptionsConstants.MinOpenInterest) & (df3['impliedVolatility'] > 0) & (df3['totalTradedVolume'] > OptionsConstants.MinTradeVolume)]
    # print(data["records"]["data"][0]["PE"]["openInterest"])
    OIMean = df3['openInterest'].mean()
    VolumneMean = df3['totalTradedVolume'].mean()
    df3 = df3[(df3['openInterest'] >= OIMean) & (df3['impliedVolatility'] > 0) & (df3['totalTradedVolume'] > VolumneMean)]
    # df3 = df3[(df3['impliedVolatility'] > 0) ]
    filemode='w'
    if(os.path.exists(OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\put_"+OptionsConstants.FileSuffix+".xlsx")):
        filemode='a'


    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\put_"+OptionsConstants.FileSuffix+".xlsx",
            engine='openpyxl',mode=filemode) as writer:
        df2.to_excel(writer,sheet_name=currSymbol, index=False)
    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\call_"+OptionsConstants.FileSuffix+".xlsx",
            engine='openpyxl',mode=filemode) as writer:
        df3.to_excel(writer,sheet_name=currSymbol, index=False)

def CreateOptionData(JsonPath,OptionType='CE'):
    with open(JsonPath) as f:
        data = json.load(f)
    df = pd.DataFrame(list(data["records"]["data"][0:]), columns=['PE', 'CE']).dropna()

    df2 = pd.DataFrame(df[OptionType].values.tolist())
    return(df2)

# latest 05/02/2021
def CreateExpectedSpotLists(OptionType,currSymbol="Sheet1"):
    data = pd.read_excel( OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"_"+OptionsConstants.FileSuffix+".xlsx",sheet_name=currSymbol)
    OutputList=[]
    for index, row in data.iterrows():
        t = OptionsConstants.TradeDate
        r = 0.1
        S = row['underlyingValue']
        sigma = float((row['impliedVolatility']) / 100)
        K = row['strikePrice']
        T = (datetime.datetime.strptime(row['expiryDate'], '%d-%b-%Y')).strftime('%d-%m-%Y')
        # default market environment
        market_env = MarketEnvironment(t, r, S, sigma)
       # define option style and type
        opt_style = "plain_vanilla"  # "digital" # "plain_vanilla"
        opt_type =OptionType
        option = option_factory(market_env, opt_style, opt_type, K, T)
        ProjectedPriceList = CalcualtePricesForRange(S, option)
        OutputList.append(
            {'OptionType': OptionType, 'StrikePrice': row['strikePrice'], 'Underlying': row['underlyingValue'],
             'LastPrice': row['lastPrice'], 'ExpiryDate': row['expiryDate'],
             'ProjectedSpot': ProjectedPriceList})

    newCalldf = pd.DataFrame(OutputList).dropna()
    filemode = 'w'
    if (os.path.exists(OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"Projected_"+OptionsConstants.FileSuffix+".xlsx")):
        filemode = 'a'
    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"Projected_"+OptionsConstants.FileSuffix+".xlsx",
            engine='openpyxl',mode=filemode) as writer:
        newCalldf.to_excel(writer,sheet_name=currSymbol, index=False)
    return(OutputList)


def MappingForZerodha(OptionType,inpSymbol='Nifty'):
    source = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx"
    OriginalData = pd.read_excel(source)
    data = pd.read_excel(source, usecols=[OptionType+'_Expiry', OptionType+'_Strike']).drop_duplicates()
    data[OptionType+'Symbol'] = inpSymbol


    if(OptionType=='call'):
        OptionPrefix= "CE"
    else:
        OptionPrefix = "PE"
    for index, row in data.iterrows():

        Strike = row[OptionType+'_Strike']
        T = (datetime.datetime.strptime(row[OptionType+'_Expiry'], '%d-%b-%Y'))
        # Symbol = "Nifty21"
        Symbol = inpSymbol +"21"
        dt = T + relativedelta(day=31, weekday=TH(-1))
        if (T.day == dt.day):
            Symbol = Symbol + str(T.strftime('%b')) + str(Strike) +OptionPrefix
        else:
            Symbol = Symbol + str(int(T.strftime('%m'))) + str(T.strftime('%d')) + str(Strike) + OptionPrefix
        data[OptionType + 'Symbol'][index] = Symbol

    return(pd.merge(OriginalData, data))

def getOptionChain(currSymbol,testurl = "https://www.nseindia.com/api/option-chain-indices?symbol="):
    testurl=testurl+currSymbol
    filepath=OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\"+currSymbol+".json"

    try:
        os.makedirs(OptionsConstants.Location + "\\" + OptionsConstants.TradeDate)
        os.remove(filepath)
    except OSError:
        pass
    hdr = {
        # 'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Accept': '*/*'

    }

    resp = requests.get('https://www.nseindia.com', headers=hdr)
    # resp = requests.get('https://www.nseindia.com/market-data/equity-derivatives-watch', headers=hdr)
    session_id = get_session_id(resp)
    hdr = {
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'Accept': '*/*',
        'Cookie': session_id
    }
    time.sleep(1)
    data= requests.get(testurl,headers=hdr)
    # with urllib.request("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY") as url:
    #     data = json.loads(url.read().decode())
    if("expiry" not in data.text):
        raise Exception('Option chain not created')

    # with open('C:\\Users\\srepswal\\Desktop\\test.json', 'w') as outfile:
    with open(filepath, 'w') as outfile:
        outfile.write(data.text)
    # tradeObject.driver.quit()


def getOptionChainForStocks(currSymbol,testurl = "https://www.nseindia.com/api/option-chain-indices?symbol="):
    testurl=testurl+currSymbol
    filepath=OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\"+currSymbol+".json"
    url_oc = "https://www.nseindia.com/option-chain"
    url = testurl
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    # print(response.json())
    data=response

    with open(filepath, 'w') as outfile:
        outfile.write(data.text)
    # with open('C:\\Users\\srepswal\\Desktop\\test.json', 'w') as outfile:

    # tradeObject.driver.quit()

def getTopSecurities(filepath="",testurl = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"):


    url_oc = "https://www.nseindia.com/option-chain"
    url = testurl
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    data = session.get(url, headers=headers, timeout=5, cookies=cookies)

    #
    # hdr = {
    #     'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    #     'Accept': '*/*'
    #
    # }
    # resp=requests.get('https://www.nseindia.com/market-data/equity-derivatives-watch',headers=hdr)
    # session_id = get_session_id(resp)
    # hdr  ={
    #         'sec-ch-ua':'"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    #         'Accept': '*/*',
    #     'Cookie':session_id
    # }
    # data= requests.get(testurl,headers=hdr)
    # with urllib.request("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY") as url:
    #     data = json.loads(url.read().decode())
    with open('C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\ActiveStocks.json', 'w') as outfile:
        outfile.write(data.text)
    # tradeObject.driver.quit()

def getChangeInPrice(data,OptionType,NewPriceColumn):
    # data[OptionType+"_Change"] = 0
    data["Call_Change"] = 0
    data["Put_Change"] = 0
    for index, row in data.iterrows():

        prevCallPrice=row[OptionType+"Price"]
        currCallPrice = row["call_"+OptionsConstants.PriceSuffix]
        change=((currCallPrice-prevCallPrice)/prevCallPrice*100)
        # data[OptionType+"_Change"][index] =change
        data["Call_Change"][index] = change

        prevPutPrice = row["PutPrice"]
        currPutPrice = row["put_"+OptionsConstants.PriceSuffix]
        change = ((currPutPrice - prevPutPrice) / prevPutPrice * 100)
        data["Put_Change"] [index] = change


    return(data)

def getPricesFromFile(source = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_"+OptionsConstants.FileSuffix+".xlsx",currSymbol=""):
    originalList = pd.read_excel(source,sheet_name=currSymbol)
    currSymbolfilepath = OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\" + currSymbol + ".json"
    callList_updated = CreateOptionData(currSymbolfilepath, 'CE')
    originalList = pd.merge(originalList, callList_updated[['expiryDate', 'strikePrice', 'lastPrice']],
                        left_on=['call_Expiry', 'call_Strike'], right_on=['expiryDate', 'strikePrice'], how='left')
    originalList = originalList.drop(columns={'expiryDate', 'strikePrice'})
    originalList = originalList.rename(columns={"lastPrice": 'call_' + OptionsConstants.PriceSuffix})

    putList_updated = CreateOptionData(currSymbolfilepath, 'PE')
    originalList = pd.merge(originalList, putList_updated[['expiryDate', 'strikePrice', 'lastPrice']],
                        left_on=['put_Expiry', 'put_Strike'], right_on=['expiryDate', 'strikePrice'], how='left')
    originalList = originalList.drop(columns={'expiryDate', 'strikePrice'})
    originalList = originalList.rename(columns={"lastPrice": 'put_' + OptionsConstants.PriceSuffix})
    book = load_workbook(source)
    writer = pandas.ExcelWriter(source, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    originalList.to_excel(writer, sheet_name=currSymbol, index=False)
    writer.save()
    # with pd.ExcelWriter(
    #
    #         OptionsConstants.Location + "\\" + OptionsConstants.TradeDate + "\\OptionResult_" + OptionsConstants.PriceSuffix + ".xlsx",
    #         engine="xlsxwriter") as writer:
    #     originalList.to_excel(writer, index=False)

def get_session_id(resp):
    cookies_str = resp.headers['Set-Cookie']
    if cookies_str:
        for kv in cookies_str.split(';'):
            if 'webpy_session_id=' in kv:
                return kv

def CreateSpotListsWithGreeks(OptionType,currSymbol="Sheet1"):
    data = pd.read_excel( OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"_"+OptionsConstants.FileSuffix+".xlsx",sheet_name=currSymbol)
    OutputList=[]
    # OutputList[OptionType+'_Delta']=0.000000
    # OutputList[OptionType + '_Theta'] = 0.000000
    # OutputList[OptionType + '_Gamma'] = 0.000000
    # OutputList[OptionType + '_Vega'] = 0.000000
    # OutputList[OptionType + '_Rho'] = 0.000000
    for index, row in data.iterrows():
        t = OptionsConstants.TradeDate
        r = 0.1
        S = row['underlyingValue']
        sigma = float((row['impliedVolatility']) / 100)
        K = row['strikePrice']
        T = (datetime.datetime.strptime(row['expiryDate'], '%d-%b-%Y')).strftime('%d-%m-%Y')
        # default market environment
        market_env = MarketEnvironment(t, r, S, sigma)
       # define option style and type
        opt_style = "plain_vanilla"  # "digital" # "plain_vanilla"
        opt_type =OptionType
        option = option_factory(market_env, opt_style, opt_type, K, T)
        Delta = option.delta()
        Theta = option.theta()
        Gamma = option.gamma()
        Vega = option.vega()
        Rho = option.rho()

        OutputList.append(
            {'OptionType': OptionType, 'StrikePrice': row['strikePrice'], 'Underlying': row['underlyingValue'],
             'LastPrice': row['lastPrice'], 'ExpiryDate': row['expiryDate'],
             OptionType + '_Delta': '%.4f'%float(option.delta()[0]),
             OptionType + '_Theta': '%.4f'%float(option.theta()[0]),
             OptionType + '_Gamma': '%.4f'%float(option.gamma()[0]),
             OptionType + '_Vega': '%.4f'%float(option.vega()[0]),
             OptionType + '_Rho': '%.4f'%float(option.rho()[0])

             })

    newCalldf = pd.DataFrame(OutputList).dropna()
    filemode = 'w'
    if (os.path.exists(OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"Greeks"+OptionsConstants.FileSuffix+".xlsx")):
        filemode = 'a'
    with pd.ExcelWriter(
            OptionsConstants.Location+"\\"+OptionsConstants.TradeDate+"\\"+OptionType+"Greeks"+OptionsConstants.FileSuffix+".xlsx",
            engine='openpyxl',mode=filemode) as writer:
        newCalldf.to_excel(writer,sheet_name=currSymbol, index=False)
    return(OutputList)

def GetOptionGreekCombination(callList,putList,currSymbol="Sheet1",operand="-",filepath =OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionGreek_"+OptionsConstants.FileSuffix+".xlsx"):
    resultList=[]

    for i in callList:
        currStrike = i['StrikePrice']
        S = i['Underlying']
        S_min = (int)(S - (S *2 / 100))
        S_max = (int)(S + (S * 2 / 100))
        if(currStrike<S_min or currStrike>S_max):
        # if (currStrike < S_min):
            continue;
        for j in putList:
            currStrike = j['StrikePrice']
            S_min = (int)(S - (S * 2 / 100))
            S_max = (int)(S + (S * 2 / 100))
            if (currStrike < S_min or currStrike > S_max):
            # if ( currStrike > S_max):
                continue;
            if(operand=="-"):
                DeltaDiff=float(Abs((Abs(i['call_Delta'])-Abs(j['put_Delta']))))
                ThetaDiff = '%.4f'%float(Abs(Abs(i['call_Theta']) - Abs(j['put_Theta'])))
                GammaDiff = '%.4f'%float(Abs(Abs(i['call_Gamma']) - Abs(j['put_Gamma'])))
                VegaDiff = '%.4f'%float(Abs(Abs(i['call_Vega']) - Abs(j['put_Vega'])))
                RhoDiff='%.4f'%float(Abs(Abs(i['call_Rho']) - Abs(j['put_Rho'])))
            else:
                DeltaDiff = '%.4f' % float(Abs((Abs(i['call_Delta']) + Abs(j['put_Delta']))))
                ThetaDiff = '%.4f' % float(Abs(Abs(i['call_Theta']) +Abs(j['put_Theta'])))
                GammaDiff = '%.4f' % float(Abs(Abs(i['call_Gamma']) + Abs(j['put_Gamma'])))
                VegaDiff = '%.4f' % float(Abs(Abs(i['call_Vega']) + Abs(j['put_Vega'])))
                RhoDiff = '%.4f' % float(Abs(Abs(i['call_Rho']) + Abs(j['put_Rho'])))


            resultList.append({'call_Expiry':i['ExpiryDate'],
                               'call_Strike':i['StrikePrice'],

                               'CallPrice':i['LastPrice'],
                               'PutPrice': j['LastPrice'],
                               'put_Expiry':j['ExpiryDate'],
                               'put_Strike':j['StrikePrice'],
                               'DeltaDiff':DeltaDiff,
                                'VegaDiff':VegaDiff,
                                'GammaDiff':GammaDiff,
                                'RhoDiff' :RhoDiff,
                                'ThetaDiff'  :ThetaDiff

                               })
    resultdf = pd.DataFrame(resultList).dropna()
    filemode = 'w'
    # if (os.path.exists(OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionGreek_"+OptionsConstants.FileSuffix+".xlsx")):
    if (os.path.exists(
            filepath)):
        filemode = 'a'
    # with pd.ExcelWriter(
    #         OptionsConstants.Location + "\\" + OptionsConstants.TradeDate+"\\OptionGreek_"+OptionsConstants.FileSuffix+".xlsx",
    #         engine="openpyxl",mode=filemode) as writer:
    with pd.ExcelWriter(
               filepath,
                engine="openpyxl", mode=filemode) as writer:
        resultdf.to_excel(writer,sheet_name=currSymbol, index=False)

def main():
    # if np_output is True, the output will be np.ndarray, otherwise pd.DataFrame
    np_output = False  # True
    t = "30-04-2021"
    r = 0.10
    S = 14661
    sigma = 0.2375
    # sigma = 0.23
    K = 14600
    T = "06-05-2021"
    # default market environment
    market_env = MarketEnvironment(t,r,S,sigma)
    # print(market_env)

    # define option style and type
    opt_style = "plain_vanilla"  # "digital" # "plain_vanilla"
    opt_type = "put"  # "put"
    option = option_factory(market_env, opt_style, opt_type,K,T)
    # print(option)
    # CalcualtePricesForRange(S, option)

    # print("Metrics:")
    # print("Payoff:", option.payoff())
    # print("Price upper limit:", option.price_upper_limit())
    # print("Price lower limit:", option.price_lower_limit())
    print("Price:", option.price())
    print("P&L:", option.PnL())
    print("Delta:", option.delta())
    print("Theta:", option.theta())
    print("Gamma:", option.gamma())
    print("Vega:", option.vega())
    print("Rho:", option.rho())
    # CalcualtePricesForRange(S,option)


    # ----------------------------- usage example ---------------------------------#
if __name__ == "__main__":
    main()
