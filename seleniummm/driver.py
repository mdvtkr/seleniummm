import logging
import chromedriver_autoinstaller
import os, platform
from multipledispatch import dispatch
import screeninfo
import inspect
import undetected_chromedriver as uwebdriver
import traceback

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as Exceptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from urllib3.connectionpool import log as urllib_logger

root_path = os.path.dirname(__file__)

class WebDriver:
    def __init__(self, 
                 set_download_path=None, 
                 visible=False, 
                 minimize=False, 
                 hide=False, 
                 wait_timeout_sec=10,
                 driver_path=None, 
                 lang='kr', 
                 debug_port=None) -> None:
        try:
            self.__monitors = screeninfo.get_monitors()
        except:
            self.__monitors = None

        # try undetected driver first. selenium webdriver is fallback.
        try:
            self.__init_undetected_driver(set_download_path=set_download_path, 
                                          visible=visible, 
                                          driver_path=driver_path, 
                                          lang=lang, 
                                          debug_port=debug_port)
            print('undetected_chromedriver initialized.')
        except:
            print(traceback.format_exc())
            print('undetected_chromedriver init failed. fallback to standard selenium')
            self.__init_selenium_driver(set_download_path=set_download_path, 
                                        visible=visible, 
                                        driver_path=driver_path, 
                                        lang=lang, 
                                        debug_port=debug_port)
        print('dbg port: ' + str(debug_port))
            
        self.hide = hide
        if self.hide:
            self.wnd_hidden()
        self.minimize = minimize
        if self.minimize:
            self.wnd_min()

        self.set_wait_timeout(wait_timeout_sec)
    
    def __init_selenium_driver(self, 
                               set_download_path=None, 
                               visible=False, 
                               driver_path=None, 
                               lang='kr', 
                               debug_port=None):
        self.update_driver(driver_path)

        if set_download_path is None:
            set_download_path = root_path

        options = webdriver.ChromeOptions()
        if not visible: 
            # options.headless = True
            options.add_argument('--headless')
        if self.__monitors != None:
            options.add_argument(f'--window-size={self.__monitors[0].width},{self.__monitors[0].height}')
        else:
            options.add_argument(f'--window-size=1920,1080')
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        chrome_options = None

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')

        if debug_port is not None:  # usually 9222
            # chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_experimental_option('debuggerAddress', f'localhost:{debug_port}')
            options.add_argument(f'--remote-debugging-port={debug_port}')
        options.add_argument("--lang=" + lang)

        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
        options.add_experimental_option("prefs", {
            "download.default_directory": set_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        })
        selenium_logger.setLevel(logging.WARNING)
        urllib_logger.setLevel(logging.WARNING)

        self.driver = webdriver.Chrome(options=options, chrome_options=chrome_options)

        # print("userAgent: " + self.script('return navigator.userAgent') + "\n\n")

    def __init_undetected_driver(self, 
                                 set_download_path=None, 
                                 visible=False, 
                                 driver_path=None, 
                                 lang='kr', 
                                 debug_port=None):
        if set_download_path is None:
            set_download_path = root_path

        options = uwebdriver.ChromeOptions()
        if not visible: 
            # options.headless = True
            options.add_argument('--headless')
        if self.__monitors != None:
            options.add_argument(f'--window-size={self.__monitors[0].width},{self.__monitors[0].height}')
        else:
            options.add_argument(f'--window-size=1920,1080')
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')

        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')

        if debug_port is not None:  # usually 9222
            # chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_experimental_option('debuggerAddress', f'localhost:{debug_port}')
            options.add_argument(f'--remote-debugging-port={debug_port}')
        options.add_argument("--lang=" + lang)

        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("prefs", {
            "download.default_directory": set_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        })

        self.driver = uwebdriver.Chrome(options)

    def close(self):
        self.driver.close()

    def script(self, s):
        return self.driver.execute_script(s)
    
    def page_down(self):
        self.find_element(tag='body').send_keys(Keys.PAGE_DOWN)
    
    def page_up(self):
        self.find_element(tag='body').send_keys(Keys.PAGE_UP)

    def quit(self):
        if self.driver != None:
            self.driver.quit()
            self.driver = None

    def wnd_size(self, w,h):
        self.driver.set_window_size(w,h)

    def wnd_pos(self, x,y):
        self.driver.set_window_position(x, y)

    def wnd_hidden(self):
        monitors = screeninfo.get_monitors()
        max_h=0
        for m in monitors:
            max_h = max_h if m.height<max_h else m.height
        self.wnd_pos(0, max_h-10)

    def wnd_min(self):
        self.driver.minimize_window()

    def wnd_max(self):
        self.driver.maximize_window()

    def __del__(self):
        if self.driver is not None:
            self.quit()

    def set_wait_timeout(self, sec):
        self.__wait_timeout = sec

    def get(self, url):
        self.driver.get(url)
        if self.minimize:
            self.wnd_min()

    def open_new_tab(self):
        self.script('window.open("about:blank")')
        self.switch_to_window(idx=len(self.driver.window_handles)-1)
        if self.minimize:
            self.wnd_min()

    def get_current_url(self) -> str:
        return self.driver.current_url

    def update_driver(self, driver_path):
        # install selenium chrome driver
        path = './chromedriver'
        if driver_path is not None:
            path = driver_path
            
        if not os.path.isdir(path):
            os.makedirs(path)

        print('chromedriver: ' + chromedriver_autoinstaller.install(False, driver_path))

    @dispatch(WebElement)
    def mouse_over(self, element):            
        ActionChains(self.driver).move_to_element(element).perform()

    @dispatch(cls=str, id=str, xpath=str, name=str, css=str, tag=str, element_idx=int)
    def mouse_over(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None, element_idx=0):        
        elems = self.find_elements(cls=cls, id=id, xpath=xpath, name=name, css=css, tag=tag)
        if elems == None or len(elems) == 0 or len(elems) < element_idx:
            return
        
        self.mouse_over(element=elems[element_idx])

    @dispatch(WebElement, open_new_tab=bool)
    def click(self, element:WebElement, open_new_tab:bool=False):
        wnd_cnt = len(self.driver.window_handles)
        if open_new_tab:
            # linux/windows: control, mac: command
            cmdkey = Keys.COMMAND if 'darwin' in platform.system().lower() else Keys.COMMAND
            try:
                ActionChains(self.driver).key_down(cmdkey).click(element).key_up(cmdkey).perform()
            except:
                ActionChains(self.driver).send_keys(cmdkey + Keys.ENTER).perform()
        else:
            try:
                element.click()
            except Exceptions.ElementClickInterceptedException:
                element.send_keys(Keys.ENTER)      # sometimes exception happens

        # seems that window resize/move/focused when new tab popups up.
        if self.minimize and wnd_cnt != len(self.driver.window_handles):
            self.wnd_min()

    @dispatch(cls=str, id=str, xpath=str, name=str, css=str, tag=str, open_new_tab=bool)
    def click(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None, open_new_tab=False):
        elem = self.find_element(cls=cls, id=id, xpath=xpath, name=name, css=css, tag=tag)
        if elem == None:
            return
        
        self.click(elem, open_new_tab=open_new_tab)

    @dispatch(cls=str, id=str, xpath=str, name=str, css=str, tag=str)
    def find_element(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return None

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

    @dispatch(WebElement, cls=str, id=str, xpath=str, name=str, css=str, tag=str)
    def find_element(self, element, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe(), 2, 2):
            return None

        if cls:
            return element.find_element(By.CLASS_NAME, cls)
        elif id:
            return element.find_element(By.ID, id)
        elif xpath:
            return element.find_element(By.XPATH, xpath)
        elif name:
            return element.find_element(By.NAME, name)
        elif css:
            return element.find_element(By.CSS_SELECTOR, css)
        elif tag:
            return element.find_element(By.TAG_NAME, tag)
        else:
            return None
        
    @dispatch(WebElement, cls=str, id=str, xpath=str, name=str, css=str, tag=str)
    def find_elements(self, element, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe(), 2, 2):
            return []
        
        if cls:
            return element.find_elements(By.CLASS_NAME, cls)
        elif id:
            return element.find_elements(By.ID, id)
        elif xpath:
            return element.find_elements(By.XPATH, xpath)
        elif name:
            return element.find_elements(By.NAME, name)
        elif css:
            return element.find_elements(By.CSS_SELECTOR, css)
        elif tag:
            return element.find_elements(By.TAG_NAME, tag)
        else:
            return []

    @dispatch(cls=str, id=str, xpath=str, name=str, css=str, tag=str)
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

    def find_children(self, element, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe(), at_least=2, at_most=2):   # find all
            return element.find_elements(By.XPATH, './/*')
        elif cls:
            return element.find_elements(By.CLASS_NAME, cls)
        elif id:
            return element.find_elements(By.ID, id)
        elif xpath:
            return element.find_elements(By.XPATH, xpath)
        elif name:
            return element.find_elements(By.NAME, name)
        elif css:
            return element.find_elements(By.CSS_SELECTOR, css)
        elif tag:
            return element.find_elements(By.TAG_NAME, tag)
        else:
            return []

    def select(self, element, index=None, text=None, value=None):
        if not self.__inserted_param_check__(inspect.currentframe(), 2, 2):
            print('error param')
            return False
        try:
            sel_elem = Select(element)
            if index:
                sel_elem.select_by_index(index)
            elif text:
                sel_elem.select_by_visible_text(text)
            elif value:
                sel_elem.select_by_value(value)
            else:
                return False
            return True
        except Exception as e:
            print('select error: ' + repr(e))
            return False

    def confirm(self, ok=True):
        alert = self.wait_until_alert_visible()

        do = alert.accept if ok else alert.dismiss
        print(f'confirm popup: {alert.text} -> {do.__name__}')
        do()

    def sleep(self, seconds):
        self.driver.implicitly_wait(seconds)


    def wait_until_alert_visible(self):
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.alert_is_present())

    def wait_until_element_visible(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.visibility_of_element_located(condition))
    
    def wait_until_elements_visible(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.visibility_of_all_elements_located(condition))

    def wait_until_element_clickable(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.element_to_be_clickable(condition))

    def wait_until_element_invisible(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return
        
        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.invisibility_of_element(condition))
    
    def wait_until_window_number_to_be(self, n):
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.number_of_windows_to_be(n))


    def switch_to_window(self, idx):
        self.driver.switch_to.window(self.driver.window_handles[idx])
        if self.minimize:
            self.wnd_min()

    def switch_to_frame(self, idx=None, frame=None):
        if not self.__inserted_param_check__(inspect.currentframe(), at_least=0):
            return
        
        if idx:
            self.driver.switch_to.frame(idx)
        elif frame:
            self.driver.switch_to.frame(frame)
        else:
            self.driver.switch_to.default_content()

    
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

    def __get_param_list__(self, inspect_frame):
        arg_info = inspect.getargvalues(inspect_frame)
        return [ arg_info[3][key] for key in arg_info[0][1:] ]
    
    def __inserted_param_check__(self, inspect_frame, at_least=1, at_most=1):
        params = self.__get_param_list__(inspect_frame)
        inserted_count = len(params) - params.count(None)
        if inserted_count < at_least:
            print('too little params')
            return False
        elif inserted_count > at_most:
            print('too many params')
            return False
        return True