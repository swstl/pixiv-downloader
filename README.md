# Pixiv Bookmark Fetcher and Downloader

This project provides a passive tool that occasionally checks for new bookmarks added by the user, fetch those bookmarks, and download the bookmarked artworks.

---

## Usage

### Install:

1. Clone the repository:
   ```bash
   git clone https://github.com/Dogfetus/pixiv-downloader.git
   cd pixiv-downloader
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Command:
```bash
python main.py [OPTIONS]
```

### CLI Options:
| Option            | Type   | Description                                                    |
|-------------------|--------|----------------------------------------------------------------|
| `--save_path`     | string | Path to save downloaded artworks.                              |
| `--log_path`      | string | Path to save JSON logs.                                       |
| `--cookies_path`  | string | Path to user cookies JSON file for Pixiv login.                |
| `--no_folder`     | flag   | Disables saving artworks in separate folders.                  |
| `--delay_min`     | int    | Minimum delay between bookmark checks (default: 60 seconds).   |
| `--delay_max`     | int    | Maximum delay between bookmark checks (default: 120 seconds).  |
| `--timeout`       | int    | Request timeout in seconds (default: 10 seconds).              |
| `--max_threads`   | int    | Maximum concurrent download threads.                           |

### Example Command:
```bash
python main.py --save_path ./downloads --cookies_path ./cookies.json --delay_min 30 --delay_max 90
```

## OR Run with docker compose

```yaml
version: "3.8"

services:
  pixiv:
    image: dogfetus/pixiv-passive-downloader:latest
    command: >
      --save_path /app/data
      --log_path /app/user
      --cookies_path /app/user/cookies.json
      --delay_min 60 
      --delay_max 120 
      --max_threads 5
      --no_folder
    volumes:
      - <path to folder to store bookmarks>:/app/data
      - .:/app/user
    restart: unless-stopped 
```

---

## Configuration
This program uses cookies to fetch the bookmarks from the user (to log in as the user).

### Cookie File Example:
```json
[
    {
        "name": "PHPSESSID",
        "value": "your_session_id_here",
        "domain": ".pixiv.net",
        "path": "/",
        "secure": true,
        "httpOnly": true,
        "expiry": 12111111111
    },
    {
        "name": "device_token",
        "value": "your_device_token_here",
        "domain": ".pixiv.net",
        "path": "/",
        "secure": true,
        "httpOnly": true,
        "expiry": 12111111111 
    }
]
```

> **Note:** Cookies are essential for login (to fetch the bookmarks for a user). Use a browser extension like [cookie-editor](https://cookie-editor.com/) to export cookies.


---

## Troubleshooting
- **Login Issues:** Ensure the cookies file is valid and not expired.
- **No Internet Warning:** Confirm that your network connection is stable.
- **Failed Downloads:** Retry with valid bookmarks or check for changed Pixiv page structures.
- **Bookmark Mismatch:** Delete existing logs and re-run the script.

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments
- Pixiv for providing the platform.
- Selenium and Requests libraries for web automation and API handling.

> **Disclaimer:** This tool is intended for personal use.


