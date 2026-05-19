import sys
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class Logger:
    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def info(msg: str):
        print(f"{Fore.BLUE}[INFO] [{Logger._get_timestamp()}] {msg}")

    @staticmethod
    def success(msg: str):
        print(f"{Fore.GREEN}[SUCCESS] [{Logger._get_timestamp()}] {msg}")

    @staticmethod
    def warning(msg: str):
        print(f"{Fore.YELLOW}[WARNING] [{Logger._get_timestamp()}] {msg}")

    @staticmethod
    def error(msg: str):
        print(f"{Fore.RED}[ERROR] [{Logger._get_timestamp()}] {msg}", file=sys.stderr)

    @staticmethod
    def debug(msg: str):
        print(f"{Fore.CYAN}[DEBUG] [{Logger._get_timestamp()}] {msg}")
