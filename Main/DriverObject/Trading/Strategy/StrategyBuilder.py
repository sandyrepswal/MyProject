import os

import pandas as pd
import datetime as dt
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import yfinance as yf
from statsmodels.tsa.stattools import adfuller

from Main.DriverObject.Trading.Strategy import PairConstants


class StrategyBuilder:

    def __init__(self):
        self.driver = None

    def readData(self, Filepath):
        df=pd.read_csv(Filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        count_df = pd.DataFrame(df.Name.value_counts()[:470], columns=["Name", "Count"]).reset_index()
        list_valid_shares = list(count_df["index"])
        final_df = df[df.Name.isin(list_valid_shares)]
        final_df.head()
        data_by_year = final_df.groupby("Year")
        data_2020 = data_by_year.get_group(2020)
        pivot_df = data_2020.pivot(index="Date", columns="Name", values="Close")
        corr_mat = pivot_df.corr(method='pearson').apply(lambda x: x.abs())
        sorted_corr = corr_mat.unstack().sort_values(kind="quicksort", ascending=False)
        sc = pd.DataFrame(sorted_corr, columns=["Name"])
        destination=r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv"
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        sorted_corr.to_csv(destination,index=True)

    def readData2(self, Filepath):
        df = pd.read_csv(Filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        d = dict(tuple(df.groupby(['Name','Year'])))
        for key in  d.keys():
            df1=d[key]
            y=df1[["Adj Close"]].to_numpy()
            for key_child in  d.keys():
                if(key==key_child):
                    continue
                if(key[0]==key_child[0] or key[1]!=key_child[1] ):
                    continue
                df2=d[key_child]
                x = df2[["Adj Close"]].to_numpy()
                x = sm.add_constant(x)
                # model = LinearRegression().fit(x, y)
                # print('coefficient of determination:', model.score(x,y))
                # print('intercept:', model.intercept_)
                # print('slope:', model.coef_)
                model_new = sm.OLS(y, x)
                results = model_new.fit()
                print("dependent:{} child :{} year: {}",key[0],key_child[0],key[1])
                print(results.params) # min is slope and max is intercept
                #bse maxis std error of intercept

                print(results.summary())

                print(np.sqrt(results.scale)) #standad error of residuals

    def GetDataYahoo(self,symbolList,destination):
        # data = yf.download("EICHERMOT.NS TVSMOTOR.NS", start="2017-01-01", end="2017-04-30",
        #                    group_by="ticker")
        # data = yf.download("EICHERMOT.NS TVSMOTOR.NS", period="2y")
        data = yf.download(symbolList, period="2y")
        # destination = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv"
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        data.to_csv(destination, index=True)

    def getLinearData(self,Filepath):
        df = pd.read_csv(Filepath, header=[0, 1])

        df.columns = df.columns.map('_'.join)
        df.rename_axis('Date').reset_index()
        for currCol in df.columns:
            if("Date" in currCol ):
                df.rename(columns={currCol: 'Date'}, inplace=True)
                break
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        d = dict(tuple(df.groupby(['Year'])))
        for key in d.keys():
            df1 = d[key]
            for currCol in df.columns:
                if("Adj" in currCol):
                    y_Security=currCol
                    y=df1[y_Security].to_numpy()
                    for currChildCol in df.columns:
                        if ("Adj" in currChildCol and currCol!=currChildCol  ):
                            x_Security=currChildCol
                            x = df1[x_Security].to_numpy()
                            x_withConstant = sm.add_constant(x)
                            model_new = sm.OLS(y, x_withConstant)
                            results = model_new.fit()
                            print("")
                            print("dependent:", y_Security," child is:",x_Security,"year is :", key)
                            print("coefficient and slope are:",results.params)  # min is slope and max is intercept
                            print("standard error of intercept is :",results.bse[0])
                            # bse maxis std error of intercept
                            print("r-squared value is:",results.rsquared)
                            # print(results.summary())

                            print(np.sqrt(results.scale))  # standad error of residuals
                            errRatio =results.bse[0]/results.scale
                            print("error Ratio is:",errRatio)
                            xy=np.corrcoef(x, y)
                            yx = np.corrcoef(y, x)
                            print("correlation of x and y is ",xy)
                            print("correlation of y and x is ", yx)

                            ResidualArray=results.resid
                            a = np.ravel(ResidualArray)
                            print("p - value = ", adfuller(a)[1])
# Date|X/Y/Coeff/intercept/intercept err/residual error/ratio of intercept to residual/adf value/residual value/ratio of residual to std error
#signal adf is less than .05, std deviation is -2 to +2 is entry, stnd deviation to -3 or +3 is exit, stnd deviation to -1 +1 is exit with profit
#close price needs to be updated daily or weekly
#backtest
#specify start date and end date
#get regression data form end date - 1 year or last avlb date
# for entire range consider same params
# get stnd deviation for each date
# looop thru data, if entry signal encountered, create a trade with paras
# date,Long security, short security , entry price of both and entry std deviation
# look for exit or stop or period end, get exit price, exit criteriam exit std deviation
#     if poritable put in proift trade
#     else put in lss trade
# in the end calcualte report total no of trades , porift trades, loss trades
#
# calculate different correlation matrices based on 2020
# for the one which have high correlation and low adf value do back test

    def getSecurityCorrData(self, sourcePath,StartDate,Enddate=datetime.today().strftime('%m/%d/%Y')):
        foLotPath = sourcePath + "\\fo_mktlots.csv"
        df_Folot = pd.read_csv(foLotPath ,header=[0])
        Filepath=sourcePath+"\\"+ PairConstants.Sector+"History.csv"
        df = pd.read_csv(Filepath, header=[0])
        # df.columns = df.columns.map('_'.join)
        # df.rename_axis('Date').reset_index()
        for currCol in df.columns:
            if ("Date" in currCol):
                df.rename(columns={currCol: 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'])
                break
        df1=  df[df["Date"].isin(pd.date_range(end=StartDate,periods=365,freq='D' ))]
        resultList=[]
        for currCol in df.columns:
            if ("Date" not in currCol):
                y_Security = currCol
                y = df1[y_Security].to_numpy()
                for currChildCol in df.columns:
                    if ("Date" not in currChildCol and currCol != currChildCol):
                        x_Security = currChildCol
                        x = df1[x_Security].to_numpy()
                        x_withConstant = sm.add_constant(x)
                        model_new = sm.OLS(y, x_withConstant)
                        results = model_new.fit()
                        xy= np.corrcoef(x, y)
                        yx = np.corrcoef(y, x)
                        # print("correlation of x and y is ", xy)
                        # print("correlation of y and x is ", yx)

                        ResidualArray = results.resid
                        a = np.ravel(ResidualArray)
                        # print("p - value = ", adfuller(a)[1])

                        try:
                            Dep_lot = df_Folot.loc[df_Folot['SYMBOL'].str.strip() == currCol.replace(".NS", ""), 'LOTSIZE'].iloc[0]
                            Indep_lot = df_Folot.loc[df_Folot['SYMBOL'].str.strip()  == currChildCol.replace(".NS",""), 'LOTSIZE'].iloc[0]
                        except:
                            Dep_lot=0
                            Indep_lot=0


                        resultList.append({"Start_Date":StartDate,"End_Date":Enddate,
                        "Dependent":currCol,"Independent":currChildCol,"Slope":results.params[1],
                        "Intercept":results.params[0],"Res_errorSD":np.sqrt(results.scale),
                         "Adf":adfuller(a)[1],"Correlation":xy[0][1],
                          "Err_Ratio":results.bse[0]/ np.sqrt(results.scale),
                                           "Dependent_Lot":Dep_lot,"Independent_Lot":Indep_lot})

        resultdf = pd.DataFrame(resultList).dropna()
        destination=sourcePath+"\\"+PairConstants.Sector+"\\CorrData_"+Enddate.replace("/","")+".csv"
        # destination = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\CorrData.csv"
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        resultdf.to_csv(destination, index=False)

    def getDataForBackTest(self, Filepath):
        df = pd.read_csv(Filepath, header=[0])
        # df.columns = df.columns.map('_'.join)
        # df.rename_axis('Date').reset_index()
        for currCol in df.columns:
            if ("Date" in currCol):
                df.rename(columns={currCol: 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'])
                break
        df1=  df[df["Date"].isin(pd.date_range(end="1/1/2021",periods=365,freq='D' ))]
        df_result=df[df["Date"].isin(pd.date_range(start="1/1/2021",end="06/07/2021"))]
        for currCol in df.columns:
            if ("Date" not in currCol):
                y_Security = currCol
                y = df1[y_Security].to_numpy()
                for currChildCol in df.columns:
                    if ("Date" not in currChildCol and currCol != currChildCol):
                        x_Security = currChildCol
                        x = df1[x_Security].to_numpy()
                        x_withConstant = sm.add_constant(x)
                        model_new = sm.OLS(y, x_withConstant)
                        results = model_new.fit()
                        print("")
                        print("dependent:", y_Security, " child is:", x_Security)
                        print("coefficient and slope are:", results.params)  # min is slope and max is intercept
                        print("standard error of intercept is :", results.bse[0])
                        # bse maxis std error of intercept
                        print("r-squared value is:", results.rsquared)
                        # print(results.summary())

                        print(np.sqrt(results.scale))  # standad error of residuals
                        errRatio = results.bse[0] / results.scale
                        print("error Ratio is:", errRatio)
                        xy = np.corrcoef(x, y)
                        yx = np.corrcoef(y, x)
                        print("correlation of x and y is ", xy)
                        print("correlation of y and x is ", yx)

                        ResidualArray = results.resid
                        a = np.ravel(ResidualArray)
                        print("p - value = ", adfuller(a)[1])
                        df_result["Slope"] = results.params[1]
                        df_result["intercept"] = results.params[0]
                        df_result["Res_errorSD"] = np.sqrt(results.scale)
                        df_result["Residual"] =0
                        df_result["Residual"]=df_result.apply(lambda row: row["B"]-(row["A"]*row["Slope"])-row["intercept"],axis=1)
                        df_result["SD"]=df_result.apply(lambda row: row["Residual"]/row["Res_errorSD"],axis=1)
        destination = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\BackTestData.csv"
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        df_result.to_csv(destination, index=True)

    def BackTest(self, Filepath):
        Filepath = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\BackTestData.csv"
        data = pd.read_csv(Filepath, header=[0])
        trades=[]
        TradeActive=False
        for index, row in data.iterrows():
            if(int(abs(row["SD"]))==2 and (TradeActive==False)):
                TradeActive=True
                entryDate=row["Date"]
                entrySD=row["SD"]
                if(row["SD"]<0):
                    Long_Security="B"
                    LongPrice=row["B"]
                    Short_Security="A"
                    ShortPrice=row["A"]*row["Slope"]
                else:
                    Long_Security = "A"
                    LongPrice = row["A"]*row["Slope"]
                    Short_Security = "B"
                    ShortPrice = row["B"]
            elif( (TradeActive==True)):
                if(int(abs(row["SD"]))==1):
                    exitReason = "Target"
                    TradeActive = False
                elif(int(abs(row["SD"]))==3):
                    exitReason = "StopLoss"
                    TradeActive = False
                if(TradeActive==False):
                    exitDate=row["Date"]
                    exitSD = row["SD"]

                    if(Long_Security == "A"):
                        LongExitPrice=row[Long_Security]*row["Slope"]
                        ShortExitPrice=row[Short_Security]
                    else:
                        LongExitPrice = row[Long_Security]
                        ShortExitPrice = row[Short_Security] * row["Slope"]
                    Pnl=(LongExitPrice-LongPrice)+(ShortPrice-ShortExitPrice)
                    trades.append({"Entry":entryDate,"EntrySD":entrySD,"Long_Security":Long_Security,
                                  "Short_Security":Short_Security,"Long_EntryPrice":LongPrice,
                                  "Short_EntryPrice":ShortPrice,"ExitDate":exitDate,"ExitSD":exitSD,
                                  "ExitReason":exitReason,"LongExitPrice":LongExitPrice,"ShortExitPrice":ShortExitPrice,
                                  "Pnl":Pnl})
        resultdf = pd.DataFrame(trades).dropna()
        destination = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\TradeResults.csv"
        # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
        resultdf.to_csv(destination, index=True)

    def BactTestData(self,sourcePath,startDate,endDate):

        # corrData = sourcePath+"\\CorrData_"+PairConstants.Sector+".csv"
        corrData = sourcePath + "\\" + PairConstants.Sector + "\\CorrData_" + endDate.replace("/","")+".csv"
        df_corrData= pd.read_csv(corrData)
        df_corrData["Trades"]=0
        df_corrData["#ProfitTrades"]=0
        df_corrData["#LossTrades"]=0
        df_corrData["minProfit"]=0
        df_corrData["maxLoss"]=0
        df_corrData["TotalProfit"]=0
        df_corrData["Investment"] = 0
        df_corrData["ProfitPercent"] = 0.0
        df_corrData["LossPercent"] = 0.0
        df_corrData["TradeFile"]=""
        Filepath= sourcePath+"\\"+ PairConstants.Sector+"History.csv"
        df = pd.read_csv(Filepath)
        for currCol in df.columns:
            if ("Date" in currCol):
                df.rename(columns={currCol: 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'])
                break

        df_BackTest = df[df["Date"].isin(pd.date_range(start=startDate, end=endDate))]
        i=1
        for index, currrow in df_corrData.iterrows():

            for currCol in df.columns:
                if(currrow["Dependent"] in currCol):
                    # df_BackTest[currCol]=df[currCol][df["Date"].isin(pd.date_range(start=startDate, end=endDate))]
                    DependentSec=currCol
                if (currrow["Independent"] in currCol):
                    # df_BackTest[currCol] = df[currCol][df["Date"].isin(pd.date_range(start=startDate, end=endDate))]
                    IndependentSec = currCol
            df_BackTest["Residual"] = df_BackTest.apply(lambda row: row[DependentSec] - (row[IndependentSec] * currrow["Slope"]) - currrow["Intercept"]
                                                   ,axis=1 )
            df_BackTest["Slope"] =currrow["Slope"]
            df_BackTest["Dependent_Lot"] = currrow["Dependent_Lot"]
            df_BackTest["Independent_Lot"] = currrow["Independent_Lot"]
            # df_BackTest["Intercept"] = currrow["Intercept"]
            df_BackTest["SD"] = df_BackTest.apply(lambda row: row["Residual"] / currrow["Res_errorSD"], axis=1)
            trades = []
            TradeActive = False
            NoOfTrades = 0
            LossTrades = 0
            ProfitTrades = 0
            minProfit = 1000000
            maxLoss = 0
            TotalProfit=0
            Dep_lot=1
            Indep_lot=1
            minInvestment=-1

            for childindex, row in df_BackTest.iterrows():
                if (int(abs(row["SD"])) == 2 and (TradeActive == False)):
                    TradeActive = True
                    NoOfTrades+=1
                    entryDate = row["Date"]
                    entrySD = row["SD"]
                    Dep_lot,Indep_lot= self.GetLotSize(row[DependentSec],row[IndependentSec],row["Dependent_Lot"],row["Independent_Lot"], row["Slope"])
                    if (row["SD"] < 0):
                        Long_Security = DependentSec
                        LongPrice = row[DependentSec]*Dep_lot
                        LongEntry=row[DependentSec]
                        ShortEntry=row[IndependentSec]
                        Short_Security = IndependentSec
                        # ShortPrice = row[IndependentSec] * row["Slope"]*Indep_lot
                        ShortPrice = row[IndependentSec] * Indep_lot
                    else:
                        Long_Security = IndependentSec
                        # LongPrice = row[IndependentSec] * row["Slope"]*Indep_lot
                        LongPrice = row[IndependentSec]  * Indep_lot
                        Short_Security = DependentSec
                        ShortPrice = row[DependentSec]*Dep_lot
                        LongEntry = row[IndependentSec]
                        ShortEntry = row[DependentSec]
                elif ((TradeActive == True)):
                    if (int(abs(row["SD"])) == 1):
                        exitReason = "Target"
                        TradeActive = False
                    elif (int(abs(row["SD"])) == 3):
                        exitReason = "StopLoss"
                        TradeActive = False
                    if (TradeActive == False):
                        exitDate = row["Date"]
                        exitSD = row["SD"]

                        if (Long_Security == IndependentSec):
                            # LongExitPrice = row[Long_Security] * row["Slope"]*Indep_lot
                            LongExitPrice = row[Long_Security] * Indep_lot
                            ShortExitPrice = row[Short_Security] *Dep_lot
                            LongExit=row[Long_Security]
                            ShortExit=row[Short_Security]
                        else:
                            LongExitPrice = row[Long_Security]*Dep_lot
                            # ShortExitPrice = row[Short_Security] * row["Slope"]*Indep_lot
                            # ShortExitPrice = row[Short_Security] * row["Slope"] * Indep_lot
                            ShortExitPrice = row[Short_Security] * Indep_lot
                            LongExit =row[Long_Security]
                            ShortExit = row[Short_Security]
                        Pnl = (LongExitPrice - LongPrice) + (ShortPrice - ShortExitPrice)
                        TotalProfit+=Pnl
                        if(Pnl>0):
                            ProfitTrades+=1
                            if(Pnl<minProfit):
                                minProfit=Pnl
                        else:
                            LossTrades+=1
                            if (Pnl < maxLoss):
                                maxLoss = Pnl
                        try:
                            if(minInvestment<((LongPrice+ShortPrice)*25/100)):
                                minInvestment = ((LongPrice+ShortPrice)*25/100)
                                if(minInvestment <=0):
                                    minInvestment = -1
                        except ZeroDivisionError:
                            minInvestment=-1
                        trades.append({"Entry": entryDate, "EntrySD": entrySD, "Long_Security": Long_Security,
                                       "Short_Security": Short_Security, "Long_EntryPrice": LongPrice,
                                       "Short_EntryPrice": ShortPrice, "ExitDate": exitDate, "ExitSD": exitSD,
                                       "ExitReason": exitReason, "LongExitPrice": LongExitPrice,
                                       "ShortExitPrice": ShortExitPrice,"LongEntry":LongEntry,"ShortEntry":ShortEntry,
                                       "LongExit":LongExit,"ShortExit":ShortExit,
                                       "Pnl": Pnl,"Min_Investment":minInvestment,
                                       "Dep_Lot":Dep_lot,"Indep_Lot":Indep_lot})
            resultdf = pd.DataFrame(trades).dropna()
            resultdf=resultdf.reindex(columns=["EntrySD","ExitSD","Entry","ExitDate","ExitReason","Long_Security","Dep_Lot",
                               "LongEntry","Long_EntryPrice","LongExit","LongExitPrice", "Short_Security","Indep_Lot","ShortEntry", "Short_EntryPrice",
                               "ShortExit", "ShortExitPrice", "Pnl","Min_Investment"])
            df_corrData["Trades"][index]=NoOfTrades
            df_corrData["#ProfitTrades"][index] = ProfitTrades
            df_corrData["#LossTrades"][index] = LossTrades
            df_corrData["minProfit"][index] = minProfit
            df_corrData["maxLoss"][index] = maxLoss
            df_corrData["TotalProfit"][index] = TotalProfit
            df_corrData["Investment"][index] = minInvestment
            df_corrData["ProfitPercent"][index]=(TotalProfit/minInvestment*100)
            df_corrData["LossPercent"][index] = (maxLoss / minInvestment * 100)
            df_corrData["TradeFile"][index] = "TradeResults"+str(i)
            try:
                os.makedirs(sourcePath + "\\" + PairConstants.Sector + "\\Backtest\\"+endDate.replace("/",""))
            except OSError:
                pass
            destination = sourcePath + "\\" + PairConstants.Sector + "\\Backtest\\"+endDate.replace("/","")+  r'\TradeResults'+str(i)+".csv"
            # destination = r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\TradeResults"+str(i)+".csv"
            # with pd.ExcelWriter(destination, engine="openpyxl",mode='a') as writer:
            resultdf.to_csv(destination, index=True)
            i+=1

        df_corrData.to_csv(corrData,index=False)

    def GetLotSize(self,Dep_Price,Indep_Price,DepLot,IndepLot,Slope):
        index_Dep=1
        index_indep=1
        i = 0
        while(True):
            i+=1
            if(Slope>1):
                # currDepValue=Dep_Price*DepLot*index_Dep
                # currIndepValue = Indep_Price * IndepLot * index_indep*Slope
                currDepValue =  DepLot * index_Dep* Slope
                currIndepValue = IndepLot * index_indep
            else:

                # currDepValue = (Dep_Price * DepLot * index_Dep)
                # currIndepValue = Indep_Price * IndepLot * index_indep
                currDepValue = ( DepLot * index_Dep)
                currIndepValue =IndepLot * index_indep/Slope
            try:
                Diffpercent=abs(currDepValue-currIndepValue)/currDepValue*100
            except:
                Diffpercent=0
            if(Diffpercent<21 or i>10):
                return (index_Dep*DepLot, index_indep*IndepLot)
                break
            if(currDepValue<currIndepValue):
                index_Dep+=1
            else:
                index_indep+=1

