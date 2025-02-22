from utils.pixiv import pixivAPI
import json

pixiv = pixivAPI()

def load_cookies(filepath):
    with open(filepath, "r") as file:
        return json.load(file)

# Load and convert cookies
cookies = load_cookies("config/cookies.json")

# Pass the cookies to the login function
pixiv.login(cookies)
# print(pixiv._request("GET", "https://www.pixiv.net/dashboard").text)
bookmarks = pixiv.bookmarks()
print(bookmarks)
if isinstance(bookmarks, list):
    print(len(bookmarks))
