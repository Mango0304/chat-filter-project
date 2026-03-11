"""导出器测试"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exporter import ChatExporter
from core.parser import ChatMessage


class TestChatExporter:
    """ChatExporter测试类"""

    @pytest.fixture
    def sample_messages(self):
        """示例消息列表"""
        return [
            ChatMessage(
                time="2024-01-01 10:00:00",
                sender="张三",
                content="借款5000元"
            ),
            ChatMessage(
                time="2024-01-01 11:00:00",
                sender="李四",
                content="已转账"
            ),
        ]

    def test_export_html(self, sample_messages):
        """测试导出HTML"""
        exporter = ChatExporter()
        html = exporter.export(
            messages=sample_messages,
            keywords=["借款", "转账"],
            mode="fuzzy"
        )

        assert "聊天记录筛选结果" in html
        assert "张三" in html
        assert "借款5000元" in html
        assert "李四" in html
        assert "已转账" in html

    def test_export_with_matched_info(self, sample_messages):
        """测试带匹配信息的导出"""
        matched_info = [
            {"matched": True, "matched_keywords": ["借款"]},
            {"matched": True, "matched_keywords": ["转账"]},
        ]

        exporter = ChatExporter()
        html = exporter.export(
            messages=sample_messages,
            keywords=["借款", "转账"],
            mode="fuzzy",
            matched_info=matched_info
        )

        assert "匹配关键词: 借款" in html
        assert "匹配关键词: 转账" in html

    def test_escape_html(self):
        """测试HTML转义"""
        exporter = ChatExporter()

        assert exporter._escape_html("<test>") == "&lt;test&gt;"
        assert exporter._escape_html("a & b") == "a &amp; b"
        assert exporter._escape_html('quote "test"') == "quote &quot;test&quot;"

    def test_save_html(self, sample_messages):
        """测试保存HTML文件"""
        exporter = ChatExporter()
        html = exporter.export(
            messages=sample_messages,
            keywords=["test"],
            mode="fuzzy"
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            exporter.save_html(html, temp_path)
            assert os.path.exists(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "聊天记录筛选结果" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_stats_display(self, sample_messages):
        """测试统计信息显示"""
        exporter = ChatExporter()
        html = exporter.export(
            messages=sample_messages,
            keywords=["借款", "转账", "还款", "汇款"],
            mode="fuzzy"
        )

        assert "2" in html  # 消息数量
        assert "借款,转账,还款..." in html  # 关键词（超过3个显示省略）

    def test_mode_display(self, sample_messages):
        """测试模式显示"""
        # fuzzy模式
        exporter = ChatExporter()
        html = exporter.export(
            messages=sample_messages,
            keywords=["test"],
            mode="fuzzy"
        )
        assert "模糊" in html

        # exact模式
        html = exporter.export(
            messages=sample_messages,
            keywords=["test"],
            mode="exact"
        )
        assert "精确" in html

    def test_empty_messages(self):
        """测试空消息列表"""
        exporter = ChatExporter()
        html = exporter.export(
            messages=[],
            keywords=["test"],
            mode="fuzzy"
        )

        assert "0" in html
        assert "筛选消息数" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
