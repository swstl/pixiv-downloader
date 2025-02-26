from utils.pixiv import pixivAPI
from utils.config import config
from datetime import datetime
import http.client as httplib
import random
import time


def internet() -> bool:
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


def main():
    cfg = config()
    pixiv = pixivAPI(cfg)
    pixiv.login_with_cookies()

    while True:
        if internet():
            bookmarks, total_bookmarks = pixiv.fetch_new_bookmarks()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Found {len(bookmarks)} new (total: {total_bookmarks}) bookmarks at {current_time}: {bookmarks}", flush=True)
            pixiv.download(bookmarks)
            pixiv.download_missing_bookmarks()
            print("Done", flush=True)
        else:
            print("No internet connection", flush=True)
        delay = random.uniform(cfg.delay_min, cfg.delay_max)
        time.sleep(delay)

if __name__ == "__main__":
    if not internet():
        print("No internet connection", flush=True)
        exit(1)
    main()

