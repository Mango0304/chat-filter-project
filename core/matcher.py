"""关键词匹配模块"""

from typing import List
from .parser import ChatMessage


class KeywordMatcher:
    """
    关键词匹配器
    支持exact/fuzzy模式
    支持any/all规则
    """

    def __init__(self, keywords: List[str], mode: str = "fuzzy", rule: str = "any"):
        """
        初始化匹配器

        Args:
            keywords: 关键词列表
            mode: 匹配模式，"exact"精确匹配 或 "fuzzy"模糊匹配
            rule: 匹配规则，"any"任意关键词匹配 或 "all"所有关键词匹配
        """
        self.keywords = [k.strip() for k in keywords if k.strip()]
        self.mode = mode
        self.rule = rule
        self._validate_params()

    def _validate_params(self) -> None:
        """验证参数合法性"""
        if self.mode not in ("exact", "fuzzy"):
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'exact' or 'fuzzy'")
        if self.rule not in ("any", "all"):
            raise ValueError(f"Invalid rule: {self.rule}. Must be 'any' or 'all'")
        if not self.keywords:
            raise ValueError("Keywords list cannot be empty")

    def match(self, message: ChatMessage) -> bool:
        """
        判断消息是否匹配关键词

        Args:
            message: 聊天消息

        Returns:
            bool: 是否匹配
        """
        # 同时匹配发送者和内容
        search_text = f"{message.sender} {message.content}"

        if self.rule == "any":
            return self._match_any(search_text)
        else:
            return self._match_all(search_text)

    def _match_any(self, text: str) -> bool:
        """任意关键词匹配"""
        for keyword in self.keywords:
            if self._keyword_match(text, keyword):
                return True
        return False

    def _match_all(self, text: str) -> bool:
        """所有关键词匹配"""
        for keyword in self.keywords:
            if not self._keyword_match(text, keyword):
                return False
        return True

    def _keyword_match(self, text: str, keyword: str) -> bool:
        """
        单个关键词匹配

        Args:
            text: 待匹配文本
            keyword: 关键词

        Returns:
            bool: 是否匹配
        """
        if self.mode == "exact":
            # 精确匹配，区分大小写
            return keyword in text
        else:
            # 模糊匹配，不区分大小写
            keyword_lower = keyword.lower()
            text_lower = text.lower()
            return keyword_lower in text_lower

    def filter_messages(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """
        过滤消息列表

        Args:
            messages: 原始消息列表

        Returns:
            List[ChatMessage]: 过滤后的消息列表
        """
        return [msg for msg in messages if self.match(msg)]

    def get_match_info(self, message: ChatMessage) -> dict:
        """
        获取消息的匹配信息

        Args:
            message: 聊天消息

        Returns:
            dict: 匹配信息，包含matched和matched_keywords
        """
        search_text = f"{message.sender} {message.content}"
        matched_keywords = []

        for keyword in self.keywords:
            if self._keyword_match(search_text, keyword):
                matched_keywords.append(keyword)

        return {
            "matched": len(matched_keywords) > 0,
            "matched_keywords": matched_keywords,
            "match_count": len(matched_keywords)
        }
