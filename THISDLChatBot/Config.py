from abc import ABC, abstractmethod
from json import JSONDecodeError

from .Logger import Logger
from .Logger import levels
import json


class ConfigValue(ABC):
    """配置文件值的类"""
    use_password = False

    def __init__(self, input_prompt: str, normal_value=None):
        """创建配置文件值的方法"""
        self.__value = None
        self.input_prompt = input_prompt
        self.normal_value = normal_value

    def get(self):
        """获取值的方法"""
        return self.__value

    def set(self, value) -> None:
        """设置值的方法"""
        if value is None:
            self.__value = None
            return
        try:
            self.__value = self.process_value(value)
        except ValueError as ve:
            if self.normal_value is None:
                raise ve
            self.__value = self.normal_value

    @abstractmethod
    def process_value(self, value):
        """处理输入值到真实值的方法"""
        pass


class IntValue(ConfigValue):
    """整数配置文件值的类"""
    def process_value(self, value):
        """处理输入至整数值的方法"""
        return int(value)


class StringValue(ConfigValue):
    """字符串配置文件值的类"""
    def process_value(self, value):
        """处理输入至字符串值的方法"""
        return str(value)


class BoolValue(ConfigValue):
    """布尔配置文件值的类"""
    def process_value(self, value):
        """处理输入至布尔值的方法"""
        if isinstance(value, bool):
            return value
        options = {
            "true": True,
            "True": True,
            "false": False,
            "False": False
        }
        if value in options:
            return options[value]
        return bool(value)


class PasswordValue(StringValue):
    """密码配置文件值的类"""
    use_password = True


class LoggerLevelValue(ConfigValue):
    """日志等级配置文件值的类"""
    def process_value(self, value):
        """处理输入至日志等级对应字符串的方法"""
        if value not in levels:
            raise ValueError("unavailable logger level")
        return value


class Config(ABC):
    """配置文件类"""
    def __init__(self, filepath: str = 'config.json', encoding: str = 'utf-8') -> None:
        """通过文件路径创建配置文件对象,默认路径为"config.json\""""
        self.filepath = filepath
        self.encoding = encoding
        self.values: dict[str, ConfigValue] = {}
        self._add_values()
        self.reload()

    @abstractmethod
    def _add_values(self):
        """添加配置文件值的方法"""
        pass

    def __getitem__(self, item):
        """获取配置文件中的值的方法"""
        return self.values.get(item).get()

    def to_dict(self) -> dict:
        """将配置文件转成json的方法"""
        res = {}
        for key, value in self.values.items():
            res[key] = value.get()
        return res

    def save(self):
        """保存配置文件的方法"""
        with open(self.filepath, 'w', encoding=self.encoding) as config:
            json.dump(self.to_dict(), config, indent=4)

    def create_guide(self, logger: Logger):
        """创建配置文件的向导方法"""
        for value in self.values.values():
            if value.get() is not None:
                continue
            if value.use_password:
                value.set(logger.password(value.input_prompt))
            else:
                value.set(logger.input(value.input_prompt))
        self.save()

    def reload(self):
        """从文件重载配置文件的方法"""
        open(self.filepath, 'a')
        with open(self.filepath, encoding=self.encoding) as config:
            try:
                json_config = json.load(config)
            except JSONDecodeError:
                json_config = {}
            for key, value in self.values.items():
                value.set(json_config.get(key))


class ChatBotConfig(Config):
    """机器人配置文件类"""
    def _add_values(self):
        """添加配置文件值的方法"""
        self.values = {
            "username": StringValue(
                "Please enter your username:",
                ""
            ),
            "password": PasswordValue(
                "Please enter your password:",
                ""
            ),
            "logger_level": LoggerLevelValue(
                "Please specify the logger level:",
                "INFO"
            ),
            "http_retry": IntValue(
                "Please specify the HTTP retry count:",
                5
            ),
            "wait_time": IntValue(
                "Please specify the wait time after receiving a message (in microseconds):",
                500
            ),
            "auto_accept": BoolValue(
                "Should auto-accept friend requests? (True/False):",
                True
            ),
            "auto_login": BoolValue(
                "Should auto-login be enabled? (True/False):",
                True
            )
        }
