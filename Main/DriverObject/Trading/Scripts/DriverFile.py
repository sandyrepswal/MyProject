import pickle
from selenium import webdriver


class DriverFile(object):
    def __init__(
        self,
        # chromedriver path
        driver_path='C:\\Users\\srepswal\\PycharmProjects\\chromedriver.exe',
        # pickle file path to store cookies
        cookies_file_path='C:/Users/srepswal/work/chrome/cookies.pkl',
        # list of websites to reuse cookies with
        cookies_websites=["https://in.tradingview.com/"]

    ):
        self.driver_path = driver_path
        self.cookies_file_path = cookies_file_path
        self.cookies_websites = cookies_websites
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(
            executable_path=self.driver_path,
            options=chrome_options
        )
        try:
            # load cookies for given websites
            cookies = pickle.load(open(self.cookies_file_path, "rb"))
            for website in self.cookies_websites:
                self.driver.get(website)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
        except Exception as e:
            # it'll fail for the first time, when cookie file is not present
            print(str(e))
            print("Error loading cookies")

    def save_cookies(self):
        # save cookies
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(self.cookies_file_path, "wb"))

    def close_all(self):
        # close all open tabs
        if len(self.driver.window_handles) < 1:
            return
        for window_handle in self.driver.window_handles[:]:
            self.driver.switch_to.window(window_handle)
            self.driver.close()

    def quit(self):
        self.save_cookies()
        self.close_all()


    def is_fb_logged_in(self):
        self.driver.get("https://in.tradingview.com/")



def fb_login(username, password):
    username_box = driver.find_element_by_id('email')
    username_box.send_keys(username)

    password_box = driver.find_element_by_id('pass')
    password_box.send_keys(password)

    login_box = driver.find_element_by_id('loginbutton')
    login_box.click()


if __name__ == '__main__':
    """
    Run  - 1
    First time authentication and save cookies

    Run  - 2
    Reuse cookies and use logged-in session
    """
    selenium_object = DriverFile()
    driver = selenium_object.driver
    selenium_object.is_fb_logged_in()

    selenium_object.quit()