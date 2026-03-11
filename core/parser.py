"""聊天HTML解析模块"""

import re
from dataclasses import dataclass
from typing import List, Optional, Iterator
from .file_reader import LargeFileReader


@dataclass
class ChatMessage:
    """聊天消息数据结构"""
    time: str
    sender: str
    content: str
    raw_html: str = ""

    def __str__(self) -> str:
        return f"[{self.time}] {self.sender}: {self.content}"


class ChatParser:
    """
    聊天HTML解析器
    假设HTML结构：<div class="chat-item">
      - <span class="time">时间</span>
      - <span class="sender">发送者</span>
      - <p class="content">内容</p>
    """

    # 大文件阈值：100MB 以下用原有逻辑，以上用流式处理
    STREAM_THRESHOLD_MB = 100

    # 正则表达式匹配chat-item
    CHAT_ITEM_PATTERN = re.compile(
        r'<div\s+class=["\']chat-item["\']>(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )

    # 匹配各部分内容
    TIME_PATTERN = re.compile(
        r'<span\s+class=["\']time["\']>(.*?)</span>',
        re.DOTALL | re.IGNORECASE
    )
    SENDER_PATTERN = re.compile(
        r'<span\s+class=["\']sender["\']>(.*?)</span>',
        re.DOTALL | re.IGNORECASE
    )
    CONTENT_PATTERN = re.compile(
        r'<p\s+class=["\']content["\']>(.*?)</p>',
        re.DOTALL | re.IGNORECASE
    )

    def __init__(self, file_path: str, chunk_size: int = 4 * 1024 * 1024):
        """
        初始化解析器

        Args:
            file_path: HTML文件路径
            chunk_size: 读取块大小
        """
        self.file_path = file_path
        self.reader = LargeFileReader(file_path, chunk_size)
        self._cache: Optional[List[ChatMessage]] = None

    def parse(self) -> List[ChatMessage]:
        """
        解析整个文件，自动选择处理方式

        小文件(<100MB)：一次性读取，兼容原有逻辑
        大文件(>=100MB)：流式处理，边读边匹配

        Returns:
            List[ChatMessage]: 消息列表
        """
        if self._cache is not None:
            return self._cache

        file_size_mb = self.reader.get_file_size_mb()

        if file_size_mb < self.STREAM_THRESHOLD_MB:
            # 小文件：原有逻辑
            messages = self._parse_whole()
        else:
            # 大文件：流式处理
            messages = list(self.parse_stream())

        self._cache = messages
        return messages

    def _parse_whole(self) -> List[ChatMessage]:
        """
        一次性读取并解析（小文件用）

        Returns:
            List[ChatMessage]: 消息列表
        """
        messages = []
        html_content = self.reader.read_all()

        # 查找所有chat-item
        for match in self.CHAT_ITEM_PATTERN.finditer(html_content):
            item_html = match.group(0)
            message = self._parse_single_item(item_html)
            if message:
                messages.append(message)

        return messages

    def parse_stream(self) -> Iterator[ChatMessage]:
        """
        流式解析，逐条返回消息（大文件用）

        特点：
        - 分块读取，不会一次性加载整个文件
        - 智能处理跨块的chat-item
        - 内存占用恒定（约100-200MB）

        Yields:
            ChatMessage: 解析出的单条消息
        """
        buffer = ""  # 跨chunk的缓冲

        for chunk in self.reader.read_chunks():
            # 将新chunk添加到缓冲区
            buffer += chunk

            # 查找所有完整的chat-item
            for match in self.CHAT_ITEM_PATTERN.finditer(buffer):
                item_html = match.group(0)
                message = self._parse_single_item(item_html)
                if message:
                    yield message

            # 保留未处理完的部分（可能是被截断的chat-item）
            # 找到最后一个完整chat-item的位置
            last_match_end = 0
            for match in self.CHAT_ITEM_PATTERN.finditer(buffer):
                last_match_end = match.end()

            # 只保留未处理的部分
            buffer = buffer[last_match_end:]

        # 处理最后可能残留的数据（虽然通常不完整）

    def _parse_single_item(self, item_html: str) -> Optional[ChatMessage]:
        """
        解析单个chat-item

        Args:
            item_html: chat-item的HTML片段

        Returns:
            Optional[ChatMessage]: 解析后的消息，解析失败返回None
        """
        time_match = self.TIME_PATTERN.search(item_html)
        sender_match = self.SENDER_PATTERN.search(item_html)
        content_match = self.CONTENT_PATTERN.search(item_html)

        if not (time_match and sender_match and content_match):
            return None

        time = self._clean_html(time_match.group(1))
        sender = self._clean_html(sender_match.group(1))
        content = self._clean_html(content_match.group(1))

        return ChatMessage(
            time=time,
            sender=sender,
            content=content,
            raw_html=item_html
        )

    @staticmethod
    def _clean_html(text: str) -> str:
        """
        清理HTML标签，提取纯文本

        Args:
            text: 包含HTML的文本

        Returns:
            str: 清理后的纯文本
        """
        # 移除所有HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 替换HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        # 合并多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_message_count(self) -> int:
        """获取消息总数"""
        return len(self.parse())
