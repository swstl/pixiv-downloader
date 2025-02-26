from utils.argparse import ArgParser
from pathlib import Path


class config:
    def __init__(self):
        self.cli_args = ArgParser().parse()
        self._use_folder = self.cli_args.no_folder if self.cli_args.no_folder is not None else True 
        self._save_path = Path(self.cli_args.save_path) if self.cli_args.save_path else Path(__file__).resolve().parents[1] / "data"
        self._log_path = Path(self.cli_args.log_path) if self.cli_args.log_path else self.save_path
        self._max_threads = self.cli_args.max_threads if self.cli_args.max_threads else 5
        self._delay_min = self.cli_args.delay_min if self.cli_args.delay_min else 60
        self._delay_max = self.cli_args.delay_max if self.cli_args.delay_max else 120
        self._timeout = self.cli_args.timeout if self.cli_args.timeout else 60
        self._cookies_path = self.cli_args.cookies_path if self.cli_args.cookies_path else Path(__file__).resolve().parents[1] / "user" / "cookies.json"
        self._max_threads = self.cli_args.max_threads if self.cli_args.max_threads else 5


    @property
    def folder(self):
        return self._use_folder

    @property
    def save_path(self):
        return self._save_path

    @property
    def log_path(self):
        return self._log_path

    @property
    def max_threads(self):
        return self._max_threads

    @property
    def delay_min(self):
        return self._delay_min
 
    @property
    def delay_max(self):
        return self._delay_max
 
    @property
    def timeout(self):
        return self._timeout

    @property
    def cookies_path(self):
        return self._cookies_path



