import logging
import chromedriver_autoinstaller
import os;
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from urllib3.connectionpool import log as urllib_logger

root_path = os.path.dirname(__file__)

def update_driver(driver_path):
    # install selenium chrome driver
    path = './chromedriver'
    if driver_path is not None:
        path = driver_path
        
    if not os.path.isdir(path):
        os.makedirs(path)

    print('chromedriver: ' + chromedriver_autoinstaller.install(False, driver_path))

def create(set_download_path=None, visible=False, driver_path=None):
    update_driver(driver_path)

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

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 800)

    print("userAgent: " + driver.execute_script('return navigator.userAgent') + "\n\n")

    return driver