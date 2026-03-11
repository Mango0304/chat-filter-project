"""关键词匹配器测试"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.matcher import KeywordMatcher
from core.parser import ChatMessage


class TestKeywordMatcher:
    """KeywordMatcher测试类"""

    @pytest.fixture
    def sample_message(self):
        """示例消息"""
        return ChatMessage(
            time="2024-01-01 10:00:00",
            sender="张三",
            content="我想借款5000元"
        )

    def test_fuzzy_match_any(self, sample_message):
        """测试模糊匹配-任意关键词"""
        matcher = KeywordMatcher(["借款", "转账"], mode="fuzzy", rule="any")
        assert matcher.match(sample_message) is True

    def test_fuzzy_match_none(self, sample_message):
        """测试模糊匹配-无匹配"""
        matcher = KeywordMatcher(["还款", "投资"], mode="fuzzy", rule="any")
        assert matcher.match(sample_message) is False

    def test_exact_match(self, sample_message):
        """测试精确匹配"""
        matcher = KeywordMatcher(["借款"], mode="exact", rule="any")
        assert matcher.match(sample_message) is True

    def test_exact_match_case_sensitive(self):
        """测试精确匹配-区分大小写"""
        message = ChatMessage(time="", sender="", content="Hello World")
        matcher = KeywordMatcher(["hello"], mode="exact", rule="any")
        assert matcher.match(message) is False

    def test_fuzzy_match_case_insensitive(self):
        """测试模糊匹配-不区分大小写"""
        message = ChatMessage(time="", sender="", content="Hello World")
        matcher = KeywordMatcher(["hello"], mode="fuzzy", rule="any")
        assert matcher.match(message) is True

    def test_rule_all(self, sample_message):
        """测试全部匹配规则"""
        # 匹配全部
        matcher = KeywordMatcher(["借款", "5000"], mode="fuzzy", rule="all")
        assert matcher.match(sample_message) is True

        # 部分匹配
        matcher = KeywordMatcher(["借款", "转账"], mode="fuzzy", rule="all")
        assert matcher.match(sample_message) is False

    def test_rule_any(self, sample_message):
        """测试任意匹配规则"""
        matcher = KeywordMatcher(["借款", "转账"], mode="fuzzy", rule="any")
        assert matcher.match(sample_message) is True

    def test_filter_messages(self):
        """测试消息过滤"""
        messages = [
            ChatMessage(time="1", sender="A", content="借款信息"),
            ChatMessage(time="2", sender="B", content="转账通知"),
            ChatMessage(time="3", sender="C", content="日常聊天"),
        ]
        matcher = KeywordMatcher(["借款", "转账"], mode="fuzzy", rule="any")
        filtered = matcher.filter_messages(messages)
        assert len(filtered) == 2

    def test_get_match_info(self):
        """测试获取匹配信息"""
        message = ChatMessage(time="", sender="", content="借款转账5000元")
        matcher = KeywordMatcher(["借款", "转账", "还款"], mode="fuzzy", rule="any")
        info = matcher.get_match_info(message)

        assert info["matched"] is True
        assert "借款" in info["matched_keywords"]
        assert "转账" in info["matched_keywords"]
        assert info["match_count"] == 2

    def test_invalid_mode(self):
        """测试无效匹配模式"""
        with pytest.raises(ValueError):
            KeywordMatcher(["test"], mode="invalid", rule="any")

    def test_invalid_rule(self):
        """测试无效匹配规则"""
        with pytest.raises(ValueError):
            KeywordMatcher(["test"], mode="fuzzy", rule="invalid")

    def test_empty_keywords(self):
        """测试空关键词列表"""
        with pytest.raises(ValueError):
            KeywordMatcher([], mode="fuzzy", rule="any")

    def test_search_in_sender(self):
        """测试搜索发送者"""
        message = ChatMessage(time="", sender="张三", content="内容")
        matcher = KeywordMatcher(["张三"], mode="fuzzy", rule="any")
        assert matcher.match(message) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
