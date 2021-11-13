from selenium import webdriver


class SeleniumDriver:
    __driverObject = None

    def __init__(self,func_Name):
        if SeleniumDriver.__driverObject is not None:
            raise Exception("Driver object cannot be initialized again")
        else:
            if func_Name == "Chrome":
                 self.get_CHROME()

    @staticmethod
    def getDriverobj(browser_Name):
        if SeleniumDriver.__driverObject is None:
            SeleniumDriver(browser_Name)
        return SeleniumDriver.__driverObject

    def get_CHROME(self):
        SeleniumDriver.__driverObject = webdriver.Chrome("C:\workspace\Training\Python\chromedriver.exe")
