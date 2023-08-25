from pathlib import Path
from tarfile import TarFile, is_tarfile
from tarfile import open as open_tar
from typing import List, Union
from zipfile import ZipFile, is_zipfile

from filetype import guess
from py7zr import SevenZipFile, is_7zfile
from rarfile import RarFile, is_rarfile


def get_file_type(file_path: Union[str, Path]) -> Union[str, None]:
    """
    Get file type of file_path
    :param file_path: path of file
    :return: file type
    """
    res = guess(file_path)
    if res is None:
        return None
    return res.extension


def requires_password(file_path: Union[str, Path]) -> bool:
    """
    Check if file requires password
    :param file_path: path of file
    :return: True if password is required, False otherwise
    """
    file_type = get_file_type(file_path)
    if file_type is None:
        return False
    if file_type == "zip":
        with ZipFile(file_path) as zf:
            for info in zf.infolist():
                if info.flag_bits & 0x1:
                    return True
    elif file_type == "rar":
        with RarFile(file_path) as rf:
            return rf.needs_password()
    elif file_type == "7z":
        with SevenZipFile(file_path) as sf:
            return sf.needs_password()
    elif file_type == "tar":
        return False
    else:
        return False


def verify_password(file_path: Union[str, Path], password: str) -> bool:
    """
    Verify password of file
    :param file_path: path of file
    :param password: password to verify
    :return: True if password is correct, False otherwise
    """
    file_type = get_file_type(file_path)
    if file_type is None:
        return False
    if file_type == "zip":
        with ZipFile(file_path) as zf:
            for info in zf.infolist():
                if info.flag_bits & 0x1:
                    try:
                        zf.open(info, pwd=password.encode())
                    except RuntimeError:
                        return False
                    return True
    elif file_type == "rar":
        with RarFile(file_path) as rf:
            file = rf.namelist()[0]
            try:
                rf.open(file, pwd=password)
            except RuntimeError:
                return False
            return True
    elif file_type == "7z":
        with SevenZipFile(file_path, password=password) as sf:
            file = sf.getnames()[0]
            try:
                sf.read(file, password=password)
            except RuntimeError:
                return False
    elif file_type == "tar":
        return True
    else:
        return False


class Info:
    def __init__(self, info, archive=None, password=None):
        self.info = info
        self.archive = archive
        self.password = password

    @property
    def is_dir(self) -> bool:
        if getattr(self.info, "is_dir", None):
            if isinstance(self.info.is_dir, bool):
                return self.info.is_dir
            return self.info.is_dir()
        elif getattr(self.info, "is_directory", None):
            return self.info.is_directory()
        elif getattr(self.info, "isdir", None):
            return self.info.isdir()

    @property
    def is_file(self) -> bool:
        if getattr(self.info, "is_file", None):
            return self.info.is_file()
        elif getattr(self.info, "isreg", None):
            return self.info.isreg()
        else:
            return not self.is_dir

    @property
    def name(self) -> str:
        if getattr(self.info, "name", None):
            return self.info.name
        elif getattr(self.info, "filename", None):
            return self.info.filename

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Info):
            return self.info == __value.info
        else:
            return self.info == __value


def list_archive(file_path: Union[str, Path], password: str = None) -> List[Info]:
    """
    List files in archive
    :param file_path: path of archive
    :param password: password of archive
    :return: list of files in archive
    """
    file_type = get_file_type(file_path)
    if file_type is None:
        return []
    if file_type == "zip":
        with ZipFile(file_path) as zf:
            return [Info(info) for info in zf.infolist()]
    elif file_type == "rar":
        with RarFile(file_path, pwd=password) as rf:
            return [Info(info) for info in rf.infolist()]
    elif file_type == "7z":
        with SevenZipFile(file_path, password=password) as sf:
            return [Info(info) for info in sf.list()]
    elif file_type == "tar":
        with open_tar(file_path, "r", encoding="utf-8") as tf:
            return [Info(info) for info in tf.getmembers()]
    else:
        return []
