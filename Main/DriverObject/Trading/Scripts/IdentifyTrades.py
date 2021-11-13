from Main.DriverObject.Trading.Scripts.Trade import Trade

T=Trade()
source = 'C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\beautifulsoup.xlsx'
destination = "C:\\Users\\srepswal\\PycharmProjects\\EquityModelling\\Main\\DriverObject\\Trading\\Data\\Trade.xlsx"
T.copyToDataExcel(source,destination)

