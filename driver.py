import logging
import chromedriver_autoinstaller
import os;
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from urllib3.connectionpool import log as urllib_logger

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import inspect

root_path = os.path.dirname(__file__)

class WebDriver:
    def __init__(self, set_download_path=None, visible=False, driver_path=None) -> None:
        self.update_driver(driver_path)

        if set_download_path is None:
            set_download_path = root_path

        options = webdriver.ChromeOptions()
        if not visible: 
            options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36')
        options.add_experimental_option("prefs", {
            "download.default_directory": set_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        })
        selenium_logger.setLevel(logging.WARNING)
        urllib_logger.setLevel(logging.WARNING)

        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1024, 800)

        print("userAgent: " + self.driver.execute_script('return navigator.userAgent') + "\n\n")

    def __del__(self):
        self.driver.close()

    def get(self, url):
        self.driver.get(url)

    def update_driver(self, driver_path):
        # install selenium chrome driver
        path = './chromedriver'
        if driver_path is not None:
            path = driver_path
            
        if not os.path.isdir(path):
            os.makedirs(path)

        print('chromedriver: ' + chromedriver_autoinstaller.install(False, driver_path))

    def find_element(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return []

        if cls:
            return self.driver.find_element(By.CLASS_NAME, cls)
        elif id:
            return self.driver.find_element(By.ID, id)
        elif xpath:
            return self.driver.find_element(By.XPATH, xpath)
        elif name:
            return self.driver.find_element(By.NAME, name)
        elif css:
            return self.driver.find_element(By.CSS_SELECTOR, css)
        elif tag:
            return self.driver.find_element(By.TAG_NAME, tag)
        else:
            return None
            
    def find_elements(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return []

        if cls:
            return self.driver.find_elements(By.CLASS_NAME, cls)
        elif id:
            return self.driver.find_elements(By.ID, id)
        elif xpath:
            return self.driver.find_elements(By.XPATH, xpath)
        elif name:
            return self.driver.find_elements(By.NAME, name)
        elif css:
            return self.driver.find_elements(By.CSS_SELECTOR, css)
        elif tag:
            return self.driver.find_elements(By.TAG_NAME, tag)
        else:
            return []
    
    def __get_ec_condition__(self, cls, id, xpath, name, css, tag):
        condition = None
        if cls:
            condition = (By.CLASS_NAME, cls)
        elif id:
            condition = (By.ID, id)
        elif xpath:
            condition = (By.XPATH, xpath)
        elif name:
            condition = (By.NAME, name)
        elif css:
            condition = (By.CSS_SELECTOR, css)
        elif tag:
            condition = (By.TAG_NAME, tag)
        return condition

    def sleep(self, seconds):
        self.driver.implicitly_wait(seconds)

    def wait_until_element_visible(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(condition))

    def wait_until_element_invisible(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(condition))
        pass


    def switch_to_frame(self, idx=None, frame=None):
        if not self.__inserted_param_check__(inspect.currentframe(), at_least=0):
            return
        
        if idx:
            self.driver.switch_to.frame(idx)
        elif frame:
            self.driver.switch_to.frame(frame)
        else:
            self.driver.switch_to.default_content()

    def __get_param_list__(self, inspect_frame):
        arg_info = inspect.getargvalues(inspect_frame)
        return [ arg_info[3][key] for key in arg_info[0][1:] ]
    
    def __inserted_param_check__(self, inspect_frame, at_least=1, at_most=1):
        params = self.__get_param_list__(inspect_frame)
        inserted_count = len(params) - params.count(None)
        if inserted_count > at_most:
            print('too many params')
            return False
        elif inserted_count < at_least:
            print('too little params')
            return False
        return True