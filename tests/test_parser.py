"""解析器测试"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser import ChatParser, ChatMessage


class TestChatParser:
    """ChatParser测试类"""

    @pytest.fixture
    def sample_html(self):
        """示例HTML内容"""
        return """<!DOCTYPE html>
<html>
<head><title>Chat</title></head>
<body>
    <div class="chat-item">
        <span class="time">2024-01-01 10:00:00</span>
        <span class="sender">张三</span>
        <p class="content">你好世界</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 11:00:00</span>
        <span class="sender">李四</span>
        <p class="content">Hello World</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 12:00:00</span>
        <span class="sender">王五</span>
        <p class="content">测试内容</p>
    </div>
</body>
</html>"""

    def test_parse_basic(self, sample_html):
        """测试基本解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_html)
            temp_path = f.name

        try:
            parser = ChatParser(temp_path)
            messages = parser.parse()
            assert len(messages) == 3
            assert messages[0].sender == "张三"
            assert messages[0].content == "你好世界"
            assert messages[1].sender == "李四"
        finally:
            os.unlink(temp_path)

    def test_parse_single_item(self):
        """测试解析单个chat-item"""
        html = """<div class="chat-item">
            <span class="time">2024-01-01</span>
            <span class="sender">Test</span>
            <p class="content">Content</p>
        </div>"""

        parser = ChatParser.__new__(ChatParser)
        message = parser._parse_single_item(html)

        assert message is not None
        assert message.time == "2024-01-01"
        assert message.sender == "Test"
        assert message.content == "Content"

    def test_clean_html(self):
        """测试HTML清理"""
        parser = ChatParser.__new__(ChatParser)

        # 测试HTML标签移除
        assert parser._clean_html("<p>Hello</p>") == "Hello"

        # 测试HTML实体
        assert parser._clean_html("&nbsp;") == ""
        assert parser._clean_html("&lt;") == "<"
        assert parser._clean_html("&gt;") == ">"
        assert parser._clean_html("&amp;") == "&"

        # 测试多余空白
        assert parser._clean_html("a   b") == "a b"

    def test_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write("<html><body></body></html>")
            temp_path = f.name

        try:
            parser = ChatParser(temp_path)
            messages = parser.parse()
            assert len(messages) == 0
        finally:
            os.unlink(temp_path)

    def test_message_count(self, sample_html):
        """测试获取消息数量"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_html)
            temp_path = f.name

        try:
            parser = ChatParser(temp_path)
            assert parser.get_message_count() == 3
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
