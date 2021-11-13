import datetime
import unittest
import json
import requests
import pandas as pd
from pyblackscholesanalytics.market.market import MarketEnvironment

from Main.DriverObject.Trading.Scripts.OptionScripts import option_factory, CalcualtePricesForRange, \
    CalculateMaxLossAndMinProfit, CalculateLossAndProfit


class OptionTest2(unittest.TestCase):
    def test_ReadURL(self):
        # url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        # # url = "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY&identifier=OPTIDXNIFTY"
        # headers = {
        #     'User-agent': 'Mozilla/5.0'
        # }
        # t = requests.get(url,headers=headers)
        # # print(t.text)
        # test = t.json()
        # # path="100%.data.expiryDate"
        # # for expiryDate in test.values():
        # #     try:
        # #         print(expiryDate)
        # #     except KeyError:
        # #         temp="dummy"
        #
        # print(test["records"]["data"])
        with open('C:\\Users\\srepswal\\Desktop\\test.json') as f:
            data = json.load(f)
        df = pd.DataFrame(list(data["records"]["data"][0:]),columns=['PE','CE']).dropna()

        df2 = pd.DataFrame(df['PE'].values.tolist())
        df2 = df2[(df2['openInterest']>2000) & (df2['impliedVolatility']>0 )& (df2['totalTradedVolume']>2000 )]

        df3 = pd.DataFrame(df['CE'].values.tolist())
        df3 = df3[(df3['openInterest'] > 2000) & (df3['impliedVolatility']>0) & (df3['totalTradedVolume']>2000 )]
        # print(data["records"]["data"][0]["PE"]["openInterest"])
        with pd.ExcelWriter("C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\02Apr2021\\temp.xlsx", engine='xlsxwriter') as writer:
            df2.to_excel(writer, index=False)
        with pd.ExcelWriter(
                "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\02Apr2021\\call.xlsx",
                engine='xlsxwriter') as writer:
            df3.to_excel(writer, index=False)

        callList = []
        for index, row in df3.iterrows():
            print(row['strikePrice'], row['lastPrice'],row['impliedVolatility'],row['expiryDate'])
            t = "26-03-2021"
            r = 0.03
            S = row['underlyingValue']
            sigma = row['impliedVolatility']/100
            K = row['strikePrice']
            T =(datetime.datetime.strptime(row['expiryDate'], '%d-%b-%Y')).strftime('%d-%m-%Y')
            # default market environment
            market_env = MarketEnvironment(t, r, S, sigma)
            # print(market_env)

            # define option style and type
            opt_style = "plain_vanilla"  # "digital" # "plain_vanilla"
            opt_type = "call"  # "put"
            option = option_factory(market_env, opt_style, opt_type, K, T)
            ProjectedPriceList =CalcualtePricesForRange(S, option)
            callList.append(
                {'OptionType': 'Call', 'StrikePrice': row['strikePrice'], 'Underlying': row['underlyingValue'],
                 'LastPrice': row['lastPrice'], 'ExpiryDate': row['expiryDate'],
                 'ProjectedSpot': ProjectedPriceList})


        newCalldf=   pd.DataFrame(callList).dropna()
        with pd.ExcelWriter(
                "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\02Apr2021\\CallProjected.xlsx",
                engine='xlsxwriter') as writer:
            newCalldf.to_excel(writer, index=False)

        putList = []
        for index, row in df2.iterrows():
            print(row['strikePrice'], row['lastPrice'], row['impliedVolatility'], row['expiryDate'])
            t = "01-04-2021"
            r = 0.03
            S = row['underlyingValue']
            sigma = row['impliedVolatility'] / 100
            K = row['strikePrice']
            T = (datetime.datetime.strptime(row['expiryDate'], '%d-%b-%Y')).strftime('%d-%m-%Y')
            # default market environment
            market_env = MarketEnvironment(t, r, S, sigma)
            # print(market_env)

            # define option style and type
            opt_style = "plain_vanilla"  # "digital" # "plain_vanilla"
            opt_type = "put"  # "put"
            option = option_factory(market_env, opt_style, opt_type, K, T)
            ProjectedPriceList = CalcualtePricesForRange(S, option)
            putList.append(
                {'OptionType': 'Put', 'StrikePrice': row['strikePrice'], 'Underlying': row['underlyingValue'],
                 'LastPrice': row['lastPrice'], 'ExpiryDate': row['expiryDate'],
                 'ProjectedSpot': ProjectedPriceList})


        newPutdf = pd.DataFrame(putList).dropna()
        with pd.ExcelWriter(
                "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Option\\02Apr2021\\PutProjected.xlsx",
                engine='xlsxwriter') as writer:
            newPutdf.to_excel(writer, index=False)
        # CalculateMaxLossAndMinProfit(callList,putList)
        CalculateLossAndProfit(callList, putList)

