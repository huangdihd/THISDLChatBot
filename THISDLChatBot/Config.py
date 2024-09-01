import os
from .Logger import Logger
from .Logger import levels
import json


class Config:
    """配置文件类"""

    def __init__(self, filepath: str = 'config.json') -> None:
        """通过文件路径创建配置文件对象,默认路径为"config.json\""""
        self.config = None
        self.filepath = filepath
        self.reload()

    def __getitem__(self, item):
        """获取配置文件中的值的方法"""
        return self.config.get(item)

    def save(self):
        """保存配置文件的方法"""
        json.dump(self.config, open(self.filepath, 'w', encoding='utf-8'), indent=4)

    def create_guide(self, logger: Logger):
        """创建配置文件的向导方法"""
        logger.warn("缺少配置文件或配置文件缺少值,启动配置文件创建程序!")
        if not os.path.exists(self.filepath) or "username" not in json.load(open(self.filepath)):
            username = logger.input("输入用户名:")
            while username == "":
                logger.error("没有输入任何内容!")
                username = logger.input("输入用户名:")
        else:
            username = json.load(open(self.filepath))["username"]
        if not os.path.exists(self.filepath) or "password" not in json.load(open(self.filepath)):
            password = logger.password("请输入密码(不显示):")
            while password == "":
                logger.error("没有输入任何内容!")
                password = logger.password("请输入密码(不显示):")
        else:
            password = json.load(open("config.json"))["password"]
        if not os.path.exists(self.filepath) or "logger_level" not in json.load(open(self.filepath)):
            while True:
                logger_level = logger.input("日志等级,默认INFO:")
                if logger_level == "":
                    logger_level = "iNFO"
                    break
                if logger_level in levels:
                    break
        else:
            logger_level = json.load(open(self.filepath))["logger_level"]
        if not os.path.exists(self.filepath) or "http_retry" not in json.load(open(self.filepath)):
            http_retry = logger.input("http请求失败后的重试次数,默认5:")
            if http_retry == "":
                http_retry = 5
            else:
                while True:
                    try:
                        http_retry = int(http_retry)
                        break
                    except ValueError:
                        logger.error("错误:该值不是数字!")
                        http_retry = logger.input("http请求失败后的重试次数,默认5:")
        else:
            http_retry = json.load(open(self.filepath))["wait_time"]
        if not os.path.exists(self.filepath) or "wait_time" not in json.load(open(self.filepath)):
            wait_time = logger.input("输入每次获取消息的间隔时间(ms),默认500:")
            if wait_time == "":
                wait_time = 500
            else:
                while True:
                    try:
                        wait_time = int(wait_time)
                        break
                    except ValueError:
                        logger.error("错误:该值不是数字!")
                        wait_time = logger.input("输入每次获取消息的间隔时间(ms),默认500:")
        else:
            wait_time = json.load(open(self.filepath))["wait_time"]
        if not os.path.exists(self.filepath) or "auto_login" not in json.load(open(self.filepath)):
            auto_login = logger.input("是否自动重新登录(true或false),默认true:")
            if auto_login == "":
                auto_login = True
            else:
                while True:
                    if auto_login == "true":
                        auto_login = True
                        break
                    elif auto_login == "false":
                        auto_login = False
                        break
                    else:
                        logger.error("错误:请输入true或false:!")
                        auto_login = logger.input("是否自动重新登录(true或false),默认true:")
        else:
            auto_login = json.load(open(self.filepath))["auto_login"]
        if not os.path.exists(self.filepath) or "auto_accept" not in json.load(open(self.filepath)):
            auto_accept = logger.input("是否自动同意好友申请(true或false),默认true:")
            if auto_accept == "":
                auto_accept = True
            else:
                while True:
                    if auto_accept == "true":
                        auto_accept = True
                        break
                    elif auto_accept == "false":
                        auto_accept = False
                        break
                    else:
                        logger.error("错误:请输入true或false:!")
                        auto_accept = logger.input("是否自动同意好友申请(true或false),默认true:")
        else:
            auto_accept = json.load(open(self.filepath))["auto_login"]
        self.config = {
            "username": username,
            "password": password,
            "logger_level": logger_level,
            "http_retry": http_retry,
            "wait_time": wait_time,
            "auto_login": auto_login,
            "auto_accept": auto_accept
        }
        self.save()

    def reload(self):
        """从文件重载配置文件的方法"""
        keys = ['username', 'password', 'logger_level', 'http_retry', 'wait_time', 'auto_login', 'auto_accept']
        if os.path.exists("config.json") and list(json.load(open(self.filepath)).keys()).sort() == keys.sort():
            self.config = json.load(open("config.json", encoding='utf-8'))
            return self.config
        else:
            self.config = {}
            return self.config
