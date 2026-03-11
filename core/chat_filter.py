#!/usr/bin/env python3
"""聊天记录筛选导出工具 - 主入口"""

import argparse
import sys
import os

from .parser import ChatParser
from .matcher import KeywordMatcher
from .exporter import ChatExporter


# 进度输出前缀
PROGRESS_PREFIX = "PROGRESS:"


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="聊天记录筛选导出工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python chat_filter.py --input chat.html --keywords 借款,转账 --output result.pdf
  python chat_filter.py --input chat.html --keywords "hello" --mode exact --rule all --output result.html
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入的聊天HTML文件路径"
    )

    parser.add_argument(
        "--keywords", "-k",
        required=True,
        help="关键词列表，用逗号分隔"
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["exact", "fuzzy"],
        default="fuzzy",
        help="匹配模式: exact精确匹配, fuzzy模糊匹配 (默认: fuzzy)"
    )

    parser.add_argument(
        "--rule", "-r",
        choices=["any", "all"],
        default="any",
        help="匹配规则: any任意关键词匹配, all所有关键词匹配 (默认: any)"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径 (.html 或 .pdf)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=4 * 1024 * 1024,
        help="文件读取块大小 (默认: 4MB)"
    )

    parser.add_argument(
        "--show-keywords",
        action="store_true",
        help="在输出中显示匹配的关键词"
    )

    return parser.parse_args()


def print_progress(message: str) -> None:
    """打印进度信息"""
    print(f"{PROGRESS_PREFIX} {message}", flush=True)


def validate_input_file(file_path: str) -> None:
    """验证输入文件"""
    if not os.path.exists(file_path):
        print(f"错误: 输入文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(file_path):
        print(f"错误: 输入路径不是文件: {file_path}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    """主函数"""
    args = parse_args()

    # 验证输入文件
    print_progress(f"正在验证输入文件: {args.input}")
    validate_input_file(args.input)

    # 解析关键词
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if not keywords:
        print("错误: 关键词列表为空", file=sys.stderr)
        return 1

    print_progress(f"加载关键词: {keywords}")
    print_progress(f"匹配模式: {args.mode}, 匹配规则: {args.rule}")

    # 1. 解析聊天记录
    print_progress("正在解析聊天记录...")
    try:
        parser = ChatParser(args.input, args.chunk_size)
        all_messages = parser.parse()
        total_messages = len(all_messages)
        print_progress(f"共解析 {total_messages} 条消息")
    except Exception as e:
        print(f"错误: 解析聊天记录失败: {e}", file=sys.stderr)
        return 1

    # 2. 关键词匹配
    print_progress("正在进行关键词匹配...")
    try:
        matcher = KeywordMatcher(keywords, args.mode, args.rule)
        filtered_messages = matcher.filter_messages(all_messages)
        matched_count = len(filtered_messages)
        print_progress(f"匹配到 {matched_count} 条消息")

        # 获取匹配信息
        matched_info = None
        if args.show_keywords:
            matched_info = [matcher.get_match_info(msg) for msg in filtered_messages]
    except Exception as e:
        print(f"错误: 关键词匹配失败: {e}", file=sys.stderr)
        return 1

    # 3. 导出结果
    print_progress(f"正在导出结果到: {args.output}")
    try:
        exporter = ChatExporter(args.output)
        html_content = exporter.export(
            messages=filtered_messages,
            keywords=keywords,
            mode=args.mode,
            matched_info=matched_info
        )

        # 如果输出是HTML格式
        if args.output.endswith(".html"):
            exporter.save_html(html_content, args.output)

    except Exception as e:
        print(f"错误: 导出失败: {e}", file=sys.stderr)
        return 1

    # 完成
    print_progress(f"完成! 共筛选 {matched_count}/{total_messages} 条消息")
    print(f"\n结果已保存到: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
