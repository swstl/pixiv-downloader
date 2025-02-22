from utils.data import data
from utils.web import web
import json
import time
import math
import re

ARTWORKS_PER_PAGE = 48  

class user:
    id: int = 0  
    total_bookmarks: int = 0
    bookmarks = []

class pixivAPI:
    def __init__(self, config):
        self.user = user()
        self.config = config 
        self.web = web()
        self.data = data(self.web, self.config)


    def __del__(self):
        self.web.stop()


    def login_with_cookies(self):
        with open(self.config.cookies_path, "r") as file:
            cookies = json.load(file)
        self.login(cookies)


    def login(self, cookies=None):
        if cookies:
            url = "https://www.pixiv.net/"
            self.web.goto(url)
            self.web.set_cookies(cookies)
        else:
            # preperation
            # TODO: Change to default browser
            url = "https://accounts.pixiv.net/login"
            self.web.goto(url)
            try:
                self.web.wait_for_element("XPATH", "//a[@href='/en/' and contains(text(),'Illustrations')]")
                _cookies = self.web.driver.get_cookies()
                for cookie in _cookies:
                    self.web.session.cookies.set(cookie["name"], cookie["value"])
            except Exception as e:
                print(f"User did not sign in {e}\n")

        self.userId()
        self.data.add_user(self.user.id)


    # finds all the artworks in the page (for bookmarks page)
    def _get_artworks(self):
        artworks = self.web.find_elements("TAG_NAME", "a")
        current_bookmarks = self.data.get_current_bookmarks(self.user.id)
        unique_links = [] 

        for link in artworks:
            href = link.get_attribute("href")
            if not href or "/en/artworks/" not in href or href in unique_links:
                continue

            if current_bookmarks and self._extract_artworkid(href) in current_bookmarks:  
                return unique_links, True

            unique_links.append(href)
        return unique_links, False 


    def _extract_artworkid(self, url):
        match = re.search(r'/artworks/(\d+)', url)
        if match:
            return int(match.group(1))
        return None


    def fetch_new_bookmarks(self, user_id=None, download=True):
        bookmarks = []
        if user_id:
            id = user_id
        else:
            id = self.user.id or self.userId()
        url = f"https://www.pixiv.net/en/users/{id}/bookmarks/artworks"
        try:
            self.web.goto(url)
            self.web.wait_for_element("XPATH", "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
            bookmarks = self.web.find_element("XPATH", "//div[contains(@class, 'sc-1mr081w-0')]//span")

            total_bookmarks = int(bookmarks.text) 
            bookmarks, match = self._get_artworks() 

            if (len(bookmarks) == 0):
                return bookmarks 

            pages = math.ceil(total_bookmarks / ARTWORKS_PER_PAGE)  

            for i in (i for i in range(pages - 1) if not match):
                self.web.goto(url + f"?p={i+2}") 
                self.web.wait_for_element("XPATH", "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
                bookmarks, match = self._get_artworks()
                bookmarks.extend(bookmarks)

            self.data.add_bookmarks(self.user.id, bookmarks)
            self.user.bookmarks.extend(bookmarks)
            self.user.total_bookmarks = len(self.user.bookmarks)

            print(f"Found {self.user.total_bookmarks} new bookmarks\n")
            print(f"Downloading bookmarks...{self.user.bookmarks}\n")
            if download and len(bookmarks):
                self.download(bookmarks)

        except Exception as e:
            print(f"Failed to get bookmarks {e}\n")

        return bookmarks 


    def bookmarks(self, user_id=None):
        if user_id:
            id = user_id
        else:
            id = self.user.id or self.userId()
        url = f"https://www.pixiv.net/en/users/{id}/bookmarks/artworks"
        try:
            self.web.goto(url)
            self.web.wait_for_element("XPATH", "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
            bookmarks = self.web.find_element("XPATH", "//div[contains(@class, 'sc-1mr081w-0')]//span")

            self.user.total_bookmarks = int(bookmarks.text) 
            self.user.bookmarks, match = self._get_artworks() 

            if (len(self.user.bookmarks) == 0):
                return self.user.bookmarks 

            pages = math.ceil(self.user.total_bookmarks / ARTWORKS_PER_PAGE)  

            #TODO: change to multiple threads for faster fetching
            for i in range(pages - 1):
                self.web.goto(url + f"?p={i+2}") 
                self.web.wait_for_element("XPATH", "//div[contains(@class, 'sc-rp5asc-9')]//img", 10)
                bookmarks, match = self._get_artworks()
                self.user.bookmarks.extend(bookmarks)

        except Exception as e:
            print(f"Failed to get bookmarks {e}\n")

        return self.user.bookmarks 


    def userId(self):
        url = "https://www.pixiv.net/dashboard" 
        response = self.web.request("GET", url, timeout=self.config.timeout)
        match = re.search(r'"user_id":\s*"?(\d+)"?', response.text)
        if match:
            user.id = int(match.group(1))
            return match.group(1)

        url_match = re.search(r'/users/(\d+)', response.text)
        if url_match:
            user.id = int(url_match.group(1))
            return url_match.group(1)

        return None


    # Extracts image links from the artwork page
    def _extract_img_links(self, artworkId):
        try:
            if isinstance(artworkId, str):
                url = artworkId
            else:
                url = f"https://www.pixiv.net/en/artworks/{artworkId}"
            self.web.goto(url)
            element = self.web.wait_for_any_of(
                10,
                ("CLASS_NAME", "sc-emr523-0"),
                ("CLASS_NAME", "gtm-medium-work-expanded-view")
            )

            if element.text == "Show all":
                element.click()
                self.web.wait_for_element("CLASS_NAME", "gtm-illust-work-scroll-finish-reading", 10)

            elif element.text == "Reading works":
                element.click()
                #TODO: CHANGE how you wait
                time.sleep(2)

            tags = self.web.find_elements("TAG_NAME", "a")
            img_urls = []
            for anchor in tags:
                href = anchor.get_attribute("href")
                if href is not None and "i.pximg.net/img-original/" in href:
                    img_urls.append(href)

            return img_urls


        except Exception:
            print(f"Failed to find pictures in artwork: {artworkId}\n")

        return []


    # artwork can either be a list of links, a single link or the id of the artwork 
    def download(self, artwork):
        if isinstance(artwork, list):
            for art in artwork:
                self.download(art)
            return

        try:
            links = self._extract_img_links(artwork)
            if not links:
                print(f"No image links found for artwork: {artwork}")
                return

            if isinstance(artwork, int):
                artwork_id = artwork
            elif isinstance(artwork, str):
                artwork_id = self._extract_artworkid(artwork)
            else:
                print(f"Unsupported artwork type: {type(artwork)}")
                return

            folder = str(artwork_id) if self.config.folder else "."
            referer_url = f"https://www.pixiv.net/en/artworks/{artwork_id}"
            self.web.change_session_cookie("Referer", referer_url)
            self.data.download(self.user.id, artwork_id, links, folder)

        except Exception as e:
            print(f"Failed to download artwork {artwork}: {e}")


