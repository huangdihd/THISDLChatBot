import sys
import time
import colorama
import getpass
import _io

levels = {
    "INFO": 0,
    "SUCCESS": 1,
    "WARN": 2,
    "ERROR": 3
}


class Logger:
    """日志类"""
    def __init__(self, stdout: _io.TextIOWrapper = sys.stdout,
                 stdin: _io.TextIOWrapper = sys.stdin, level: str = "INFO") -> None:
        """创建日志对象的方法"""
        self._level = levels[level]
        self.stdout = stdout
        self.stdin = stdin

    def set_level(self, level: str):
        if level not in levels:
            raise ValueError("unavailable logger level")
        self._level = levels[level]

    def _output(self, level: str, out: str):
        """输出信息的内部方法"""
        now = time.localtime()
        for i in out.split('\n'):
            self.stdout.write(
                colorama.Fore.RESET + f"{time.strftime('[%Y-%m-%d %H:%M:%S]', now)}"
                + f"[{level}]" + i + '\n')

    def info(self, out):
        """输出普通信息的方法"""
        if self._level < levels["INFO"]:
            return
        self._output(f"{colorama.Fore.BLUE}INFO{colorama.Fore.RESET}", str(out))

    def success(self, out):
        """输出成功信息的方法"""
        if self._level < levels["SUCCESS"]:
            return
        self._output(f"{colorama.Fore.GREEN}SUCCESS{colorama.Fore.RESET}", str(out))

    def warn(self, out):
        """输出警告信息的方法"""
        if self._level < levels["WARN"]:
            return
        self._output(f"{colorama.Fore.YELLOW}WARN{colorama.Fore.RESET}", str(out))

    def error(self, out):
        """输出错误信息的方法"""
        if self._level < levels["ERROR"]:
            return
        self._output(f"{colorama.Fore.RED}ERROR{colorama.Fore.RESET}", str(out))

    def input(self, out):
        """普通输入的方法"""
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
        """无回响输入的方法"""
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
