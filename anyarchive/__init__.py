from pathlib import Path
from typing import Iterable, List, Union

from anyarchive.utils.archive import (
    Info,
    get_file_type,
    list_archive,
    requires_password,
    verify_password,
)


class Archive:
    def __init__(self, file_path: Union[str, Path], password: str = None):
        self.file_path = Path(file_path)
        self.password = password
        self.file_type = get_file_type(self.file_path)

    def list(self) -> List[Info]:
        """
        List files in archive
        :return: list of files in archive
        """
        return list_archive(self.file_path, self.password)

    def requires_password(self) -> bool:
        """
        Check if archive requires password
        :return: True if password is required, False otherwise
        """
        return requires_password(self.file_path)

    def verify_password(self, password: str) -> bool:
        """
        Verify password of archive
        :param password: password to verify
        :return: True if password is correct, False otherwise
        """
        return verify_password(self.file_path, password)

    def __enter__(self):
        return self

    def __repr__(self) -> str:
        return f"Archive({self.file_path})"

    def __str__(self) -> str:
        return f"Archive({self.file_path})"

    def __iter__(self) -> Iterable[Info]:
        return iter(self.list())

    def __getitem__(self, index) -> Info:
        return self.list()[index]

    def __len__(self) -> int:
        return len(self.list())

    def __contains__(self, item) -> bool:
        return item in self.list()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Archive):
            return self.file_path == __value.file_path
        else:
            return self.file_path == __value

    def __hash__(self) -> int:
        return hash(self.file_path)
