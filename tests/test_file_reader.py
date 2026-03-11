"""文件读取器测试"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_reader import LargeFileReader


class TestLargeFileReader:
    """LargeFileReader测试类"""

    def test_read_small_file(self):
        """测试读取小文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello World\nTest Content")
            temp_path = f.name

        try:
            reader = LargeFileReader(temp_path)
            content = reader.read_all()
            assert content == "Hello World\nTest Content"
            assert reader.get_file_size() > 0
        finally:
            os.unlink(temp_path)

    def test_read_chunks(self):
        """测试分块读取"""
        content = "A" * 10000
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            reader = LargeFileReader(temp_path, chunk_size=1000)
            chunks = list(reader.read_chunks())
            assert len(chunks) > 1
            assert "".join(chunks) == content
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            LargeFileReader("/nonexistent/file.txt")

    def test_get_file_size_mb(self):
        """测试获取文件大小(MB)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("X" * (1024 * 1024))  # 1MB
            temp_path = f.name

        try:
            reader = LargeFileReader(temp_path)
            size_mb = reader.get_file_size_mb()
            assert 0.9 < size_mb < 1.1  # 允许一些误差
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
