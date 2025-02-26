from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

class web:
    def __init__(self, ):
        # for requests
        self.session =  requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://www.pixiv.net/"
        })
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))


    def request(self, method, url, **kwargs):
        methods = {"GET": self.session.get, "POST": self.session.post}
        try:
            response = methods[method](url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            return http_err.response


    def change_session_cookie(self, name, value):
        self.session.cookies.set(name, value)


    def _sanitize_cookie(self, cookie):
        allowed_keys = {"name", "value", "domain", "path", "expiry", "secure", "httpOnly"}
        cleaned = {k: v for k, v in cookie.items() if k in allowed_keys}

        if "expirationDate" in cookie:
            cleaned["expiry"] = int(cookie["expirationDate"])

        return cleaned


    def set_cookies(self, cookies):
        for cookie in cookies:
            co = self._sanitize_cookie(cookie)
            self.session.cookies.set(co["name"], co["value"])

