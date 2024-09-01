class LoginFailedException(Exception):
    """机器人登录失败的异常"""


class UpLoadFileFailedException(Exception):
    """机器人上传文件失败的异常"""


class HttpResponseException(Exception):
    """机器人http返回异常的异常"""
