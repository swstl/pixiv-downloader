from utils.pixiv import pixivAPI
from utils.config import config

config = config()
pixiv = pixivAPI(config)
pixiv.login_with_cookies()


print(pixiv.fetch_new_bookmarks())

