import unittest

from Main.DriverObject.Trading.Strategy import PairConstants
from Main.DriverObject.Trading.Strategy.StrategyBuilder import StrategyBuilder


class TestStrategy(unittest.TestCase):
   
    
    def test_loadData(self):
        objStrategy= StrategyBuilder()

        with open(PairConstants.SymbolPath, 'r') as f:
                for currSymbol in f:
                    currSymbol = currSymbol.replace('\n', "")
                    PairConstants.SymbolList+=currSymbol+" "
        PairConstants.SymbolList=PairConstants.SymbolList.strip()
        # objStrategy.readData2(r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityData.csv")
        objStrategy.GetDataYahoo(PairConstants.SymbolList,PairConstants.SourcePath+r"\BankHistory.csv")
        # objStrategy.getDataForBackTest(
        #     r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv")
        # objStrategy.BackTest(
        #     r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv")
        # objStrategy.getSecurityCorrData( r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv","1/1/2021")
        # FilePath= r"C:\Users\srepswal\PycharmProjects\EquityModelling\Main\DriverObject\Trading\Data\SecurityCorrData.csv"
        # objStrategy.BactTestData(FilePath,"1/1/2021","06/07/2021")



    #get historical data for specific sectors for last years
    def test_getHistoricdata(self):
        PairConstants.SymbolPath = PairConstants.SourcePath + '\\' + PairConstants.Sector + ".txt"
        objStrategy = StrategyBuilder()
        with open(PairConstants.SymbolPath, 'r') as f:
                for currSymbol in f:
                    currSymbol = currSymbol.replace('\n', "")
                    PairConstants.SymbolList+=currSymbol+" "
        PairConstants.SymbolList=PairConstants.SymbolList.strip()
        # PairConstants.SymbolList = "SBIN.NS"
        objStrategy.GetDataYahoo(PairConstants.SymbolList,PairConstants.SourcePath+"\\"+ PairConstants.Sector+"History.csv")

    def test_BackTest(self):
        objStrategy = StrategyBuilder()
        startDate=PairConstants.StartDate
        endDate=PairConstants.EndDate
        objStrategy.getSecurityCorrData(
            PairConstants.SourcePath,
            startDate,endDate)
        objStrategy.BactTestData(PairConstants.SourcePath,startDate, endDate)