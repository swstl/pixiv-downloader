import argparse

class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Application with CLI arguments and config support."
        )
        self._setup_arguments()

    def _setup_arguments(self):
        # Paths
        self.parser.add_argument("--save_path", type=str, help="Path to the folder where artworks will be saved")
        self.parser.add_argument("--log_path", type=str, help="Path to the folder where a json log will be saved")
        self.parser.add_argument("--cookies_path", type=str, help="Path to user cookies to sign in to pixiv")

        # Options
        self.parser.add_argument("--no_folder", action="store_false", help="Disable saving artworks in folders")
        
        # Requests
        self.parser.add_argument("--delay_min", type=int, help="Minimum delay (in seconds) between bookmark checks (default: 60s)")
        self.parser.add_argument("--delay_max", type=int, help="Maximum delay (in seconds) between bookmark checks (default: 120s)")
        self.parser.add_argument("--timeout", type=int, help="Request timeout in seconds (default: 10)")

        # Downloads
        self.parser.add_argument("--max_threads", type=int, help="Maximum number of downloading threads (max number of artworks downloaded at the same time)")

    def parse(self):
        """Parse the command-line arguments."""
        return self.parser.parse_args()

