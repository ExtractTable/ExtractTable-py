"""
To validate the files at Client End; Fail Faster
"""
import typing as ty
import os
from ..exceptions import ClientFileError


class CheckFile:
    __SUPPORTED_EXTENSIONS__: tuple = tuple({'.pdf', '.jpeg', '.jpg', '.png'})
    __THRESHOLD_SIZE__: int = 4      # Megabytes

    def __init__(self, filepath: ty.Union[os.PathLike, str]):
        self.filepath = filepath
        self.type_error()
        self.size_error()

    def type_error(self) -> ty.Union[Exception, None]:
        """To check file extension"""
        if self.filepath.lower().endswith(self.__SUPPORTED_EXTENSIONS__):
            return
        raise ClientFileError(Message=f"Allowed file types are {self.__SUPPORTED_EXTENSIONS__}")

    def size_error(self) -> ty.Union[Exception, None]:
        # 1027 to create some buffer
        if os.stat(self.filepath).st_size <= self.__THRESHOLD_SIZE__*1027*1027:
            return
        raise ClientFileError(Message=f"File Size greater than the threshold {self.__THRESHOLD_SIZE__} Mb.")
