"""
Create custom exceptions and warnings here
"""


class ServiceError(Exception):
    """Raise a Service Side error based on the response received"""
    def __init__(self, dict_resp: dict = None):
        print("-#- "*10)
        print("-"*9 + "Error Server Response" + "-"*9)
        self.resp = dict_resp
        for k, v in self.resp.items():
            print(f"{k}: {v}")
            self.__setattr__(k, v)
        print("-#- "*10)

    def __str__(self) -> str:
        _msg_ = ''
        if self.resp.get('Message', ''):
            _msg_ = self.resp.get('Message', '')
        else:
            _msg_ = self.resp.get('message', '')
        return str(_msg_)


class ClientFileSizeError(Exception):
    """Raise a Client Side error based on the file to be processed"""
    def __init__(self, **kwargs):
        self.resp = kwargs

    def __str__(self) -> str:
        _msg_ = ''
        if self.resp.get('Message', ''):
            _msg_ = self.resp.get('Message', '')
        else:
            _msg_ = self.resp.get('message', '')
        return str(_msg_)


class ClientFileTypeError(Exception):
    """Raise a Client Side error based on the file to be processed"""
    def __init__(self, **kwargs):
        self.resp = kwargs

    def __str__(self) -> str:
        _msg_ = ''
        if self.resp.get('Message', ''):
            _msg_ = self.resp.get('Message', '')
        else:
            _msg_ = self.resp.get('message', '')
        return str(_msg_)
