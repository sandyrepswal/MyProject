from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumDriver:
    __driverObject = None

    def __init__(self, func_Name):
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

    @staticmethod
    def launchWebsite(browser_Name,url):
        SeleniumDriver.getDriverobj(browser_Name)
        SeleniumDriver.__driverObject.get(url)
        SeleniumDriver.__driverObject.maximize_window()
        return SeleniumDriver.__driverObject

    def get_CHROME(self):
        chrome_options = Options()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
        chrome_options.add_argument('user-agent={0}'.format(user_agent))
        chrome_options.add_argument("--incognito")
        SeleniumDriver.__driverObject = webdriver.Chrome('C:\\Users\\srepswal\\PycharmProjects\\chromedriver.exe',chrome_options=chrome_options)
