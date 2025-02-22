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
