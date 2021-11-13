from Main.DriverObject import SeleniumDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By




driver = SeleniumDriver.SeleniumDriver.getDriverobj("Chrome")

driver = SeleniumDriver.SeleniumDriver.getDriverobj("Chrome")
driver.get("http://www.bseIndia.com")
driver.find_element_by_id("getquotesearch").send_keys("Yes bank")
linkelem = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//li/a/strong[contains(text(),'YES BANK')]"))
        )
linkelem.click()
# print("size is")
# print(len(linkelem))
# print(linkelem[0].get_attribute("Text"))

#driver.quit()