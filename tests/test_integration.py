"""集成测试"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_reader import LargeFileReader
from core.parser import ChatParser
from core.matcher import KeywordMatcher
from core.exporter import ChatExporter


class TestIntegration:
    """集成测试类"""

    @pytest.fixture
    def sample_chat_html(self):
        """示例聊天HTML"""
        return """<!DOCTYPE html>
<html>
<head><title>聊天记录</title></head>
<body>
    <div class="chat-item">
        <span class="time">2024-01-01 09:00:00</span>
        <span class="sender">张三</span>
        <p class="content">早上好</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 10:00:00</span>
        <span class="sender">李四</span>
        <p class="content">我想借款10000元急用</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 10:05:00</span>
        <span class="sender">张三</span>
        <p class="content">好的，我转账给你</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 10:10:00</span>
        <span class="sender">李四</span>
        <p class="content">收到转账了，谢谢</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 11:00:00</span>
        <span class="sender">王五</span>
        <p class="content">晚上一起吃饭</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 12:00:00</span>
        <span class="sender">赵六</span>
        <p class="content">还款日到了</p>
    </div>
    <div class="chat-item">
        <span class="time">2024-01-01 13:00:00</span>
        <span class="sender">李四</span>
        <p class="content">我会按时还款的</p>
    </div>
</body>
</html>"""

    def test_full_workflow_fuzzy_any(self, sample_chat_html):
        """完整工作流测试 - 模糊匹配+任意规则"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_chat_html)
            temp_path = f.name

        try:
            # 1. 解析
            parser = ChatParser(temp_path)
            messages = parser.parse()
            assert len(messages) == 7

            # 2. 匹配
            matcher = KeywordMatcher(["借款", "转账"], mode="fuzzy", rule="any")
            filtered = matcher.filter_messages(messages)
            assert len(filtered) == 3  # 包含"借款"或"转账"的消息

            # 3. 导出
            exporter = ChatExporter()
            html = exporter.export(filtered, ["借款", "转账"], "fuzzy")

            assert "3" in html  # 筛选结果数量
            assert "张三" in html
            assert "李四" in html

        finally:
            os.unlink(temp_path)

    def test_full_workflow_fuzzy_all(self, sample_chat_html):
        """完整工作流测试 - 模糊匹配+全部规则"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_chat_html)
            temp_path = f.name

        try:
            parser = ChatParser(temp_path)
            messages = parser.parse()

            # 匹配包含"借款"和"还款"的消息
            matcher = KeywordMatcher(["借款", "还款"], mode="fuzzy", rule="all")
            filtered = matcher.filter_messages(messages)
            assert len(filtered) == 0

        finally:
            os.unlink(temp_path)

    def test_full_workflow_exact(self, sample_chat_html):
        """完整工作流测试 - 精确匹配"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(sample_chat_html)
            temp_path = f.name

        try:
            parser = ChatParser(temp_path)
            messages = parser.parse()

            # 精确匹配"借款"
            matcher = KeywordMatcher(["借款"], mode="exact", rule="any")
            filtered = matcher.filter_messages(messages)
            assert len(filtered) == 1
            assert "借款" in filtered[0].content

        finally:
            os.unlink(temp_path)

    def test_large_file_streaming(self):
        """大文件流式处理测试"""
        # 生成大量聊天记录
        html_parts = ['<!DOCTYPE html><html><body>']
        for i in range(100):
            html_parts.append(f'''<div class="chat-item">
                <span class="time">2024-01-01 10:{i:02d}:00</span>
                <span class="sender">用户{i}</span>
                <p class="content">消息内容{i} 借款</p>
            </div>''')
        html_parts.append('</body></html>')

        html_content = "".join(html_parts)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name

        try:
            # 使用流式读取
            reader = LargeFileReader(temp_path, chunk_size=1000)
            chunks = list(reader.read_chunks())
            assert len(chunks) > 1

            # 解析
            parser = ChatParser(temp_path)
            messages = parser.parse()
            assert len(messages) == 100

            # 匹配
            matcher = KeywordMatcher(["借款"], mode="fuzzy", rule="any")
            filtered = matcher.filter_messages(messages)
            assert len(filtered) == 100

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
