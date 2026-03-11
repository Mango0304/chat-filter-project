"""超大文件流式读取模块"""

import os
from typing import Iterator, Optional


class LargeFileReader:
    """超大文件流式读取器，使用yield返回chunk"""

    def __init__(self, file_path: str, chunk_size: int = 4 * 1024 * 1024):
        """
        初始化文件读取器

        Args:
            file_path: 文件路径
            chunk_size: 每次读取的块大小，默认4MB
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._validate_file()

    def _validate_file(self) -> None:
        """验证文件是否存在且可读"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not os.path.isfile(self.file_path):
            raise ValueError(f"Not a file: {self.file_path}")
        if not os.access(self.file_path, os.R_OK):
            raise PermissionError(f"File not readable: {self.file_path}")

    def read_chunks(self) -> Iterator[str]:
        """
        流式读取文件，每次返回一块

        Yields:
            str: 文件的一块内容
        """
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def read_all(self) -> str:
        """
        读取整个文件（适用于小文件）

        Returns:
            str: 文件全部内容
        """
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def get_file_size(self) -> int:
        """获取文件大小（字节）"""
        return os.path.getsize(self.file_path)

    def get_file_size_mb(self) -> float:
        """获取文件大小（MB）"""
        return self.get_file_size() / (1024 * 1024)
