from utils.pixiv import pixivAPI
from utils.config import config
import random
import time

def main():
    cfg = config()
    pixiv = pixivAPI(cfg)
    pixiv.login_with_cookies()

    while True:
        bookmarks = pixiv.fetch_new_bookmarks()
        print(f"Found {len(bookmarks)} new bookmarks.")
        delay = random.uniform(cfg.delay_min, cfg.delay_max)
        time.sleep(delay)

if __name__ == "__main__":
    main()

