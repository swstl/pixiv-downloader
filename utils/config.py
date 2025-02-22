import json

class config:
    def __init__(self):
        pass


    def load_cookies(self, filepath):
        with open(filepath, "r") as file:
            return json.load(file)


    def _sanitize_cookie(self, cookie):
        allowed_keys = {"name", "value", "domain", "path", "expiry", "secure", "httpOnly"}
        cleaned = {k: v for k, v in cookie.items() if k in allowed_keys}

        if "expirationDate" in cookie:
            cleaned["expiry"] = int(cookie["expirationDate"])

        return cleaned

    def folder(self):
        # return true if folder 
        return True 
