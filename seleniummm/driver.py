import logging
import os, platform, sys
from multipledispatch import dispatch
import screeninfo
import inspect
import traceback

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as Exceptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from urllib3.connectionpool import log as urllib_logger

from tedious import intent_logger
info, dbg, err, logger = intent_logger.get('seleniummm')

root_path = os.path.dirname(__file__)

webdriver=None
uwebdriver=None

class WebDriver:
    def __import_submodule(self, use_wire):
        if use_wire:
            from seleniumwire import webdriver as wd
            import seleniumwire.undetected_chromedriver as uwd
        else:
            from selenium import webdriver as wd
            import undetected_chromedriver as uwd

        global webdriver, uwebdriver
        webdriver = wd
        uwebdriver = uwd

    def __init__(self, 
                 set_download_path=None, 
                 disable_download=False,
                 visible=False, 
                 minimize=False, 
                 hide=False, 
                 wait_timeout_sec=10,
                 driver_preference=None,
                 driver_path=None, 
                 lang='kr', 
                 debug_port=None,
                 use_wire=False) -> None:
        self.__import_submodule(use_wire)
        selenium_logger.setLevel(logging.WARNING)
        urllib_logger.setLevel(logging.WARNING)

        if set_download_path is None:
            set_download_path = root_path

        try:
            self.__monitors = screeninfo.get_monitors()
        except:
            self.__monitors = None

        def create_option(undetected:bool):
            if undetected:
                options = uwebdriver.ChromeOptions()
            else:
                options = webdriver.ChromeOptions()

            if not visible: 
                options.add_argument('--headless')
            if self.__monitors != None:
                options.add_argument(f'--window-size={self.__monitors[0].width},{self.__monitors[0].height}')
            else:
                options.add_argument(f'--window-size=1920,1080')
            options.add_argument('-ignore-certificate-errors')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument("--auto-open-devtools-for-tabs")
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')
            # options.add_argument('--user-data-dir="~/Library/Application Support/Google/Chrome/Default"')

            if not undetected:
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')

            if debug_port is not None:  # usually 9222
                options.add_argument(f'--remote-debugging-port={debug_port}')
            options.add_argument("--lang=" + lang)
            options.add_argument('--disable-dev-shm-usage')

            # chrome://prefs-internals/
            prefs = {
                "download.default_directory": set_download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "plugins.always_open_pdf_externally": True
            }
            if disable_download:
                prefs['download.download_restrictions'] = 3
            options.add_experimental_option("prefs", prefs)
            return options

        self.driver = None
        # when chromedriver needs to be selected forcibly...
        # webdriver_service = Service('./chromedriver/chromedriver')
        # self.driver = webdriver.Chrome(options=options, service=webdriver_service)
        if driver_preference == 'standard':
            self.driver = webdriver.Chrome(service=Service(), options=create_option(False))
            info('chromedriver(standard) initialized')
        elif driver_preference == 'undetected':
            self.driver = uwebdriver.Chrome(options=create_option(True))
            info('chromedriver(undetected) initialized')
        else:
            # try undetected driver first. selenium webdriver is fallback.
            try:
                self.driver = uwebdriver.Chrome(options=create_option(True))
            except:
                print(traceback.format_exc())
                err('undetected_chromedriver init failed. fallback to standard selenium')
                self.driver = webdriver.Chrome(service=Service(), options=create_option(False))
                info('chromedriver(standard) initialized')
                
        if self.driver == None:
            raise Exception('driver initialization error.')

        # if not visible:
        #     # def interceptor(request):
        #     #     required_headers = {
        #     #         'sec-ch-ua-arch': 'x86',
        #     #         'sec-ch-ua-bitness': '64',
        #     #         'sec-ch-ua-full-version': '123.0.6312.107',
        #     #         'sec-ch-ua-full-version-list': '"Google Chrome";v="123.0.6312.107", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.107"'
        #     #     }

        #     #     for key in request.headers.keys():
        #     #         if key.casefold() == 'sec-ch-ua' and 'headless' in request.headers[key].casefold():
        #     #             org = request.headers[key]
        #     #             del request.headers[key]
        #     #             request.headers[key] = org.replace('Headless', '').replace('headless', '').replace('HEADLESS', '')
        #     #         elif key.casefold() in required_headers.keys():
        #     #             required_headers.pop(key.casefold())
                
        #     #     for key in required_headers.keys():
        #     #         request.headers[key] = required_headers[key]
                    
        #     self.driver.request_interceptor = interceptor

        info('port: ' + str(debug_port))
            
        self.hide = hide
        if self.hide:
            self.wnd_hidden()
        self.minimize = minimize
        if self.minimize:
            self.wnd_min()

        self.set_wait_timeout(wait_timeout_sec)
    
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
        last_wnd_cnt = len(self.driver.window_handles)
        self.driver.switch_to.new_window('tab')
        self.wait_until_window_number_to_be(last_wnd_cnt+1)
        if self.minimize:
            self.wnd_min()

    def get_current_url(self) -> str:
        return self.driver.current_url
    
    def get_cookies(self, backup_path=None):
        cookies = self.driver.get_cookies()
        if backup_path:
            if 'time' not in sys.modules:
                import time
            if 'json' not in sys.modules:
                import json
            if 'Path' not in sys.modules:
                from pathlib import Path

            p = Path(backup_path)
            p.mkdir(mode=0o744, parents=True, exist_ok=True)
            file_name = f'{self.get_current_url()}.{time.strftime("%Y%m%d-%H%M%S", time.localtime())}.json'
            with (p/file_name).open('w') as f:
                json.dump(cookies, f)
        return self.driver.get_cookies()

    @dispatch(WebElement)
    def mouse_over(self, element):            
        ActionChains(self.driver).move_to_element(element).perform()

    @dispatch(cls=str, id=str, xpath=str, name=str, css=str, tag=str, element_idx=int)
    def mouse_over(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None, element_idx=0):        
        elems = self.find_elements(cls=cls, id=id, xpath=xpath, name=name, css=css, tag=tag)
        if elems == None or len(elems) == 0 or len(elems) < element_idx:
            return
        
        self.mouse_over(elems[element_idx])
    
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
        
    @dispatch(ShadowRoot, cls=str, id=str, xpath=str, name=str, css=str, tag=str)
    def find_element(self, shadow, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe(), 2, 2):
            return None

        if cls:
            return shadow.find_element(By.CLASS_NAME, cls)
        elif id:
            return shadow.find_element(By.ID, id)
        elif xpath:
            return shadow.find_element(By.XPATH, xpath)
        elif name:
            return shadow.find_element(By.NAME, name)
        elif css:
            return shadow.find_element(By.CSS_SELECTOR, css)
        elif tag:
            return shadow.find_element(By.TAG_NAME, tag)
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
        
    @dispatch(ShadowRoot, cls=str, id=str, xpath=str, name=str, css=str, tag=str)
    def find_elements(self, shadow, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe(), 2, 2):
            return []
        
        if cls:
            return shadow.find_elements(By.CLASS_NAME, cls)
        elif id:
            return shadow.find_elements(By.ID, id)
        elif xpath:
            return shadow.find_elements(By.XPATH, xpath)
        elif name:
            return shadow.find_elements(By.NAME, name)
        elif css:
            return shadow.find_elements(By.CSS_SELECTOR, css)
        elif tag:
            return shadow.find_elements(By.TAG_NAME, tag)
        else:
            return []
        
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
            err('error param')
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
            err('select error: ' + repr(e))
            return False

    def confirm(self, ok=True):
        alert = self.wait_until_alert_visible()

        do = alert.accept if ok else alert.dismiss
        info(f'confirm popup: {alert.text} -> {do.__name__}')
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
    
    def wait_until_element_presence(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.presence_of_element_located(condition))
    
    def wait_until_elements_presence(self, cls=None, id=None, xpath=None, name=None, css=None, tag=None):
        if not self.__inserted_param_check__(inspect.currentframe()):
            return

        condition = self.__get_ec_condition__(cls, id, xpath, name, css, tag)
        return WebDriverWait(self.driver, self.__wait_timeout).until(EC.presence_of_all_elements_located(condition))
    
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


    def switch_to_window(self, idx=0):
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

    def expand_shadow_root(self, element):
        return self.driver.execute_script('return arguments[0].shadowRoot', element)
    
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
        # params.count(None) does not work for ShadowRoot. 
        # count() seems == for check equality.
        # But ShadowRoot does not support None check using ==, supports 'is'/'is not' only. 
        inserted_count = len(params) - len([x for x in params if x is None])
        if inserted_count < at_least:
            dbg('too little params')
            return False
        elif inserted_count > at_most:
            dbg('too many params')
            return False
        return True

# FOR TEST
# if __name__ == '__main__':
#     driver = WebDriver(visible=True,
#                         driver_preference='standard',
#                        use_wire=False)