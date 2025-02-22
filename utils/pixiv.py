from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import math
import re

class user:
    id: int = 0  
    total_bookmarks: int = 0
    bookmarks = []

class pixivAPI:


    def __init__(self):
        # for requests
        self.user = user()
        self.session = requests.Session()
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


    def __del__(self):
        self.driver.quit()


    def _request(self, method, url, **kwargs):
        methods = {"GET": self.session.get, "POST": self.session.post}
        response = methods[method](url, **kwargs)
        response.raise_for_status()
        return response

    
    def _wait_for_element(self, by, selector, sec=300):
        wait = WebDriverWait(self.driver, sec)
        def present(by, selector):
            return EC.presence_of_element_located((by, selector))
        return wait.until(present(by, selector))


    def _sanitize_cookie(self, cookie):
        allowed_keys = {"name", "value", "domain", "path", "expiry", "secure", "httpOnly"}
        cleaned = {k: v for k, v in cookie.items() if k in allowed_keys}

        if "expirationDate" in cookie:
            cleaned["expiry"] = int(cookie["expirationDate"])

        return cleaned


    def login(self, cookies=None):

        if cookies:
            url = "https://www.pixiv.net/"
            self.driver.get(url)
            for cookie in cookies:
                co = self._sanitize_cookie(cookie)
                self.session.cookies.set(co["name"], co["value"])
                self.driver.add_cookie(co)
        else:
            # preperation
            # TODO: Change to default browser
            url = "https://accounts.pixiv.net/login"
            self.driver.get(url)
            try:
                self._wait_for_element(By.XPATH, "//a[@href='/en/' and contains(text(),'Illustrations')]")
                _cookies = self.driver.get_cookies()
                for cookie in _cookies:
                    self.session.cookies.set(cookie["name"], cookie["value"])
            except Exception as e:
                print(f"User did not sign in {e}\n")

    def _get_artworks(self):
        artworks = self.driver.find_elements(By.TAG_NAME, "a")
        unique_links = set()
        for link in artworks:
            href = link.get_attribute("href")
            if href and "/en/artworks/" in href:
                unique_links.add(href)
        return list(unique_links)


    def bookmarks(self, user_id=None):
        if user_id:
            id = user_id
        else:
            id = self.user.id or self.userId()
        url = f"https://www.pixiv.net/en/users/{id}/bookmarks/artworks"
        try:
            self.driver.get(url)
            self._wait_for_element(By.XPATH, "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
            bookmarks = self.driver.find_element(By.XPATH, "//div[contains(@class, 'sc-1mr081w-0')]//span")

            self.user.total_bookmarks = int(bookmarks.text) 
            self.user.bookmarks = self._get_artworks() 

            if (len(self.user.bookmarks) == 0):
                return self.user.total_bookmarks

            pages = math.ceil(self.user.total_bookmarks / 48)  

            #TODO: change to multiple threads for faster fetching
            for i in range(pages-1):
                self.driver.get(url + f"?p={i+2}") 
                self._wait_for_element(By.XPATH, "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
                self.user.bookmarks.extend(self._get_artworks())

            return self.user.bookmarks 

        except Exception as e:
            print(f"Failed to get bookmarks {e}\n")

        return self.user.total_bookmarks 


    def userId(self):
        url = "https://www.pixiv.net/dashboard" 
        response = self._request("GET", url)
        match = re.search(r'"user_id":\s*"?(\d+)"?', response.text)
        if match:
            user.id = int(match.group(1))
            return match.group(1)

        url_match = re.search(r'/users/(\d+)', response.text)
        if url_match:
            user.id = int(url_match.group(1))
            return url_match.group(1)

        return None


    def search(self, query):
        # Search for images
        # Returns a list of image URLs
        pass


    def download(self, url, path):
        # Download an image
        # Returns True if successful
        # Returns False if failed
        pass
