from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
import requests

class web:
    def __init__(self, ):
        self.by_mapping = {
            "ID": By.ID,
            "NAME": By.NAME,
            "CLASS_NAME": By.CLASS_NAME,
            "TAG_NAME": By.TAG_NAME,
            "CSS_SELECTOR": By.CSS_SELECTOR,
            "XPATH": By.XPATH,
            "LINK_TEXT": By.LINK_TEXT,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
        }


        # for requests
        self.session =  requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://www.pixiv.net/"
        })
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))


        # for selenium
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        self.options.add_argument("referer=https://www.pixiv.net/")
        self.driver = webdriver.Firefox(options=self.options)



    def request(self, method, url, **kwargs):
        methods = {"GET": self.session.get, "POST": self.session.post}
        response = methods[method](url, **kwargs)
        response.raise_for_status()
        return response


    def change_session_cookie(self, name, value):
        self.session.cookies.set(name, value)


    def wait_for_element(self, by, selector, sec=300):
        wait = WebDriverWait(self.driver, sec)
        def present(by, selector):
            return EC.presence_of_element_located((by, selector))
        return wait.until(present(self.by_mapping[by], selector))


    def wait_for_any_of(self, sec=10, *selectors):
        wait = WebDriverWait(self.driver, sec)
        conditions = []
        for by, selector in selectors:
            conditions.append(EC.presence_of_element_located((self.by_mapping[by], selector)))
        return wait.until(EC.any_of(*conditions))


    def find_elements(self, by, selector):
        return self.driver.find_elements(self.by_mapping[by], selector)


    def find_element(self, by, selector):
        return self.driver.find_element(self.by_mapping[by], selector)


    def goto(self, url):
        return self.driver.get(url)


    def get_cookies(self):
        return self.driver.get_cookies()


    def _sanitize_cookie(self, cookie):
        allowed_keys = {"name", "value", "domain", "path", "expiry", "secure", "httpOnly"}
        cleaned = {k: v for k, v in cookie.items() if k in allowed_keys}

        if "expirationDate" in cookie:
            cleaned["expiry"] = int(cookie["expirationDate"])

        return cleaned


    def set_cookies(self, cookies):
        for cookie in cookies:
            co = self._sanitize_cookie(cookie)
            self.session.cookies.set(co["name"], co["value"])
            self.driver.add_cookie(co)


    def stop(self):
        self.driver.quit()

