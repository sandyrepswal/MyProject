import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains

from Main.DriverObject import SeleniumDriver as SD

driver = SD.SeleniumDriver.launchWebsite("Chrome","https://web.stockedge.com/scan-groups")
listOfHeading=driver.find_elements_by_css_selector("ion-grid[class*='horizontal']")
mytext = open("Headings.txt", "w+", encoding="utf-8")
for heading in listOfHeading:
    mytext.writelines(heading.text+"\n")
    actionChains = ActionChains(driver)
    actionChains.move_to_element(heading).click().perform()
    time.sleep(1)
    listOfsubHeading=driver.find_elements_by_css_selector("ion-item[class*='no-padding']")
    for subheading in listOfsubHeading:
        mytext.writelines(subheading.text+"\n")
        actionChains = ActionChains(driver)
        actionChains.move_to_element(subheading).click().perform()
        time.sleep(1)
        listOfscans = driver.find_elements_by_css_selector("ion-item[class^='normal-font'][button]")
        for scan in listOfscans:
            mytext.writelines(scan.text+"\n")
            actionChains = ActionChains(driver)
            actionChains.move_to_element(scan).click().perform()
            time.sleep(1)
            mytext.writelines(driver.current_url+"\n")

            try:
                driver.find_elements_by_css_selector("button[class ='button-native sc-ion-back-button-md']")[2].click()
                time.sleep(1)
            except Exception as inst:
                print("No back button 1")
                print(type(inst))
        try:
            driver.find_elements_by_css_selector("button[class ='button-native sc-ion-back-button-md']")[1].click()
            time.sleep(1)
        except Exception as inst:
            print("No back button 2")
            print(type(inst))
    try:
        driver.find_elements_by_css_selector("button[class ='button-native sc-ion-back-button-md']")[1].click()
        time.sleep(1)
    except Exception as inst:
        print("No back button 3")
        print(type(inst))

mytext.close()