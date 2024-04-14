import sys
import time
import colorama
import getpass
import _io


class Logger:
    def __init__(self, stdout: _io.TextIOWrapper = sys.stdout, stdin: _io.TextIOWrapper = sys.stdin) -> None:
        self.stdout = stdout
        self.stdin = stdin

    def success(self, out):
        out = str(out)
        now = time.localtime()
        for i in out.split('\n'):
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}]" + i + '\n')

    def info(self, out):
        out = str(out)
        now = time.localtime()
        for i in out.split('\n'):
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.BLUE}INFO{colorama.Fore.RESET}]" + i + '\n')

    def warn(self, out):
        out = str(out)
        now = time.localtime()
        for i in out.split('\n'):
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.YELLOW}WARN{colorama.Fore.RESET}]" + i + '\n')

    def error(self, out):
        out = str(out)
        now = time.localtime()
        for i in out.split('\n'):
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.RED}ERROR{colorama.Fore.RESET}]" + i + '\n')

    def input(self, out):
        out = str(out)
        now = time.localtime()
        for i in out.split('\n')[:-1]:
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.MAGENTA}INPUT{colorama.Fore.RESET}]" + i + '\n')
        stdin = sys.stdin
        sys.stdin = self.stdin
        result = input(colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                       + f"[{colorama.Fore.MAGENTA}INPUT{colorama.Fore.RESET}]" + out.split('\n')[-1])
        sys.stdin = stdin
        return result

    def password(self, out):
        out = str(out)
        now = time.localtime()
        stdout, stdin = sys.stdout, sys.stdin
        sys.stdout, sys.stdin = self.stdout, self.stdin
        for i in out.split('\n')[:-1]:
            print(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{colorama.Fore.MAGENTA}PASSWD{colorama.Fore.RESET}]" + i)
        result = getpass.getpass(
            colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
            + f"[{colorama.Fore.MAGENTA}PASSWD{colorama.Fore.RESET}]"
            + out.split('\n')[-1])
        sys.stdout, sys.stdin = stdout, stdin
        return result
