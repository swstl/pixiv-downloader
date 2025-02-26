from utils.data import data
from utils.web import web
import json
import math
import re

ARTWORKS_PER_PAGE = 48  
BM_URL = "https://www.pixiv.net/ajax/user/{}/illusts/bookmarks?tag=&offset={}&limit=100&rest=show&lang=en"
AW_PAGES_URL = "https://www.pixiv.net/ajax/illust/{}/pages"


class user:
    id: int = 0  
    total_bookmarks: int = 0
    nickname = ""
    bookmarks = []

class pixivAPI:
    def __init__(self, config):
        self.user = user()
        self.config = config 
        self.web = web()
        self.data = data(self.web, self.config)


    def login_with_cookies(self):
        with open(self.config.cookies_path, "r") as file:
            cookies = json.load(file)
        self.login(cookies)


    def login(self, cookies=None):
        if cookies:
            print("Setting cookies..." , end="", flush=True)
            self.web.set_cookies(cookies)
        else:
            print("Not supported yet")
            # preperation
            # TODO: change to default browser
            # FIXME: this does not work 
            # print("Logging in...", end="", flush=True)
            # url = "https://accounts.pixiv.net/login"
            # self.web.goto(url)
            # try:
            #     self.web.wait_for_element("XPATH", "//a[@href='/en/' and contains(text(),'Illustrations')]")
            #     _cookies = self.web.driver.get_cookies()
            #     for cookie in _cookies:
            #         self.web.session.cookies.set(cookie["name"], cookie["value"])
            # except Exception as e:
            #     print(f"User did not sign in {e}\n")

        print("\b\b\b   [DONE]")
        self.userId()
        if not self.user.id:
            print("Failed to find user")
            exit(1)

        self.data.add_user(self.user.id)
        print(f"Logged in as user: {self.user.nickname or self.user.id}\n")


    def _extract_artworkid(self, url):
        match = re.search(r'/artworks/(\d+)', url)
        if match:
            return int(match.group(1))
        return None


    # FIXME: gifs
    def fetch_new_bookmarks(self, user_id=None):
        bookmarks = []
        total_bookmarks = 0
        found_in_bookmarks = False

        if user_id:
            id = user_id
        else:
            id = self.user.id or self.userId()
        url = BM_URL.format(id, 0) 
        self.user.bookmarks, tot_bm = self.data.get_current_bookmarks(id)

        try:
            #initial request sets the total number of bookmarks
            response = self.web.request("GET", url, timeout=self.config.timeout)
            json_data = json.loads(response.text)
            total_bookmarks = int(json_data["body"]["total"])
            for work in json_data["body"]["works"]:
                work_id = int(work["id"])
                if work_id not in self.user.bookmarks:
                    bookmarks.append(work_id)
                else:
                    found_in_bookmarks = True


            # then we loop to get all the remaining bookmarks
            for i in range(1, math.ceil(total_bookmarks / 100)):
                if found_in_bookmarks:
                    break
                url = BM_URL.format(id, i*100)
                response = self.web.request("GET", url, timeout=self.config.timeout)
                json_data = json.loads(response.text)
                for work in json_data["body"]["works"]:
                    work_id = int(work["id"])
                    if work_id not in self.user.bookmarks:
                        bookmarks.append(work_id)
                    else:
                        found_in_bookmarks = True

        except Exception as e:
            print(f"Failed to get bookmarks {e}\n")

        self.data.add_bookmarks(id, bookmarks)
        return bookmarks, total_bookmarks


    def bookmarks(self, user_id=None):
        if user_id:
            id = user_id
        else:
            id = self.user.id or self.userId()
        url = BM_URL.format(id, 0) 
        try:
            #initial request sets the total number of bookmarks
            response = self.web.request("GET", url, timeout=self.config.timeout)
            json_data = json.loads(response.text)
            total_bookmarks = int(json_data["body"]["total"])
            bookmarks = [int(work["id"]) for work in json_data["body"]["works"]]

            # then we loop to get all the remaining bookmarks
            for i in range(1, math.ceil(total_bookmarks / 100)):
                url = BM_URL.format(id, i*100)
                response = self.web.request("GET", url, timeout=self.config.timeout)
                json_data = json.loads(response.text)
                bookmarks.extend([int(work["id"]) for work in json_data["body"]["works"]])

        except Exception as e:
            print(f"Failed to get bookmarks {e}\n")

        return self.user.bookmarks 


    def userId(self) -> int:
        url = "https://www.pixiv.net/dashboard" 
        response = self.web.request("GET", url, timeout=self.config.timeout)
        id_match = re.search(r'"user_id":\s*"?(\d+)"?', response.text)
        nicname_match = re.search(r'<div class="sc-4bc73760-3 jePfsr">\s*(.*?)\s*</div>', response.text)
 
        if nicname_match:
            user.nickname = nicname_match.group(1)

        if id_match:
            user.id = int(id_match.group(1))
            return int(id_match.group(1))

        url_match = re.search(r'/users/(\d+)', response.text)
        if url_match:
            user.id = int(url_match.group(1))
            return int(url_match.group(1))

        return 0 


    def test(self, artworkId):
        return self.download(artworkId)
        return self._extract_img_links(artworkId)


    # Extracts image links from the artwork page
    def _extract_img_links(self, artworkId):
        links = []
        url = AW_PAGES_URL.format(artworkId)
        try:
            response = self.web.request("GET", url, timeout=self.config.timeout)
            json_data = json.loads(response.text)
            for page in json_data["body"]:
                if page["urls"]["original"]:
                    links.append(page["urls"]["original"])
        except Exception as e:
            print(f"Failed to get image links for id: {artworkId} | {e}\n")

        return links



    # artwork can either be a list of links, a single link or the id of the artwork 
    def download(self, artwork):
        if isinstance(artwork, list):
            for art in artwork:
                self.download(art)
            return

        try:
            if isinstance(artwork, int):
                artwork_id = artwork
            elif isinstance(artwork, str):
                artwork_id = self._extract_artworkid(artwork) 
            else:
                print(f"Unsupported artwork type: {type(artwork)}")
                return

            links = self._extract_img_links(artwork_id)
            if not links:
                print(f"No image links found for artwork: {artwork_id}")
                return

            folder = str(artwork_id) if self.config.folder else "."
            self.data.download(self.user.id or self.userId(), artwork_id, links, folder)

        except Exception as e:
            print(f"Failed to download artwork {artwork}: {e}")


    def download_missing_bookmarks(self):
        missing = self.data.get_missing_bookmarks(self.user.id)
        if missing:
            self.download(missing)

