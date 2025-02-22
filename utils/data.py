from concurrent.futures import ThreadPoolExecutor
import threading
import json
import re


class data:
    def __init__(self, web, config):
        self.web = web
        self.config = config
        self.path = self.config.save_path
        self.file_path = self.config.log_path / "saved.json"
        self.path.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_threads)

        if not self.file_path.exists():
            with open(self.file_path, "w") as f:
                json.dump({"users": []}, f, indent=2)


    def __del__(self):
        self.executor.shutdown()


    def __repr__(self):
        return f"Data(path='{self.path}')"


    def _save_to_json(self, data, path=None):
        with open(path or self.file_path, "w") as f:
            json.dump(data, f, indent=2)


    def _load_from_json(self, path=None):
        with open(path or self.file_path, "r") as f:
            return json.load(f)


    def add_bookmarks(self, user_id=0, bookmarks=[]):
        data = self._load_from_json()

        user = next((user for user in data['users'] if user['id'] == user_id), None)
        if not user:
            return

        ids = []
        for bm in bookmarks:
            match = re.search(r'/artworks/(\d+)', bm)
            if match:
                ids.append(int(match.group(1)))

        new_bookmarks = [bm for bm in ids if bm not in user['bookmarks']]
        if not new_bookmarks:
            return

        user['bookmarks'] = new_bookmarks + user['bookmarks']
        user['total_bookmarks'] = len(user['bookmarks'])

        self._save_to_json(data)


    #TODO: change to a list of all bookmarks and check if it exists
    def last_bookmark(self, user_id=0):
        data = self._load_from_json()

        user = next((user for user in data['users'] if user['id'] == user_id), None)
        if not user or not user['bookmarks']:
            return

        return str(user['bookmarks'][0]) 


    def add_user(self, user_id=0):
        data = self._load_from_json()

        if any(user["id"] == user_id for user in data["users"]):
            return

        new_user = {
            "id": user_id,
            "total_bookmarks": 0,
            "total_saved_bookmarks": 0,
            "bookmarks": [],
            "saved_bookmarks": [],
        }
        data["users"].append(new_user)

        self._save_to_json(data)


    def add_saved_bookmark(self, user_id, artwork_id):
        """Adds the artwork ID to the saved bookmarks of the user in the JSON file."""
        data = self._load_from_json()

        user = next((u for u in data["users"] if u["id"] == user_id), None)
        if user:
            if artwork_id not in user["saved_bookmarks"]:
                user["saved_bookmarks"].insert(0, artwork_id) 
                user["total_saved_bookmarks"] = len(user["saved_bookmarks"])
                self._save_to_json(data)
        else:
            print(f"User with ID {user_id} not found in JSON.")


    def remove_bookmarks(self, user_id, bookmarks):
        data = self._load_from_json()
        user = next((u for u in data["users"] if u["id"] == user_id), None)
        if user:
            user["bookmarks"] = [bm for bm in user["bookmarks"] if bm not in bookmarks]
            user["total_bookmarks"] = len(user["bookmarks"])
            self._save_to_json(data)


    def remove_saved_bookmarks(self, user_id, bookmarks):
        data = self._load_from_json()
        user = next((u for u in data["users"] if u["id"] == user_id), None)
        if user:
            user["saved_bookmarks"] = [bm for bm in user["saved_bookmarks"] if bm not in bookmarks]
            user["total_saved_bookmarks"] = len(user["saved_bookmarks"])
            self._save_to_json(data)


    def get_current_bookmarks(self, user_id):
        data = self._load_from_json()
        user = next((u for u in data["users"] if u["id"] == user_id), None)
        return user["bookmarks"] if user else []


    def get_missing_bookmarks(self, user_id):
        data = self._load_from_json()
        user = next((u for u in data["users"] if u["id"] == user_id), None)
        if user:
            return [bm for bm in user["bookmarks"] if bm not in user["saved_bookmarks"]]


    def _download_list_of_images(self, user_id, artwork_id, links, folder="."):
        try:
            target_folder = self.path / folder 
            target_folder.mkdir(parents=True, exist_ok=True)

            successful_downloads = 0

            for idx, link in enumerate(links):
                try:
                    response = self.web.request("GET", link, timeout=self.config.timeout)
                    if response.status_code == 200:
                        file_extension = link.split('.')[-1].split('?')[0]
                        filename = target_folder / f"{artwork_id}_{idx}.{file_extension}"
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        successful_downloads += 1
                    else:
                        print(f"Failed to download {link} (Status: {response.status_code})")

                except Exception as e:
                    print(f"Error downloading {link}: {e}")

            if successful_downloads == len(links):
                with self.lock:
                    self.add_saved_bookmark(user_id, artwork_id)
            else:
                print(f"Downloaded files for {artwork_id}: {successful_downloads}/{len(links)}.")

        except Exception as e:
            print(f"Error handling artwork {artwork_id}: {e}")


    def download(self, userId, artwork_id, links: list, folder="."):
        data = self._load_from_json()
        user = next((u for u in data["users"] if u["id"] == userId), None)
        if user and artwork_id not in user["saved_bookmarks"]:
            self.executor.submit(self._download_list_of_images, userId, artwork_id, links, folder)
