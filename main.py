from utils.pixiv import pixivAPI
from utils.config import config
from datetime import datetime
import random
import time

def main():
    cfg = config()
    pixiv = pixivAPI(cfg)
    pixiv.login_with_cookies()

    while True:
        bookmarks = pixiv.fetch_new_bookmarks()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Found {len(bookmarks)} new bookmarks at {current_time}.", flush=True)
        delay = random.uniform(cfg.delay_min, cfg.delay_max)
        # pixiv.download_missing_bookmarks()
        time.sleep(delay)

if __name__ == "__main__":
    main()

