#!/usr/bin/env python3
"""生成50MB模拟聊天记录HTML文件"""

import argparse
import random
import os
from datetime import datetime, timedelta

# ============ 配置 ============
DEFAULT_TARGET_SIZE_MB = 50
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_FILE = os.path.join(PROJECT_ROOT, "samples", "generated", "test_chat_50mb.html")

# 聊天成员（初始6人，会被随机打乱）
MEMBERS = ["李四", "王五", "赵六", "孙七", "周八", "钱九"]

# 转账/红包模板
TRANSFER_TEMPLATES = [
    "给你转账{amount}元，看看收到了吗",
    "转账{amount}元，麻烦查收",
    "我转了{amount}元给你",
    "收到转账{amount}元",
    "转你{amount}元，微一下",
    "[微信红包]恭喜发财，大吉大利",
    "发个红包{amount}元给大家",
    "抢红包啦！{amount}元",
    "红包{amount}元，不客气",
    "给你{amount}元先用着"
]

# 短消息模板（<50字）
SHORT_MSG_TEMPLATES = [
    "在吗？",
    "好的，知道了",
    "好的，谢谢",
    "没问题",
    "可以",
    "收到",
    "知道了",
    "好的",
    "嗯嗯",
    "哈哈",
    "是啊",
    "好吧",
    "那算了",
    "随便吧",
    "随便",
    "都行",
    "你决定吧",
    "看情况吧",
    "等一下",
    "马上来",
    "在开会",
    "在忙",
    "一会儿聊",
    "先去吃饭",
    "睡觉了",
    "起床了",
    "上班路上",
    "下班了",
    "到了",
    "出发了",
    "今天天气不错",
    "吃了吗",
    "睡了吗",
    "在干嘛",
    "出去了",
    "在家呢",
    "开会中",
    "稍等",
    "快了",
    "马上",
    "等会儿",
    "不急",
    "先这样",
    "回头聊",
    "下次吧",
    "再说吧",
    "不知道",
    "随便问问"
]

# 长消息模板（>100字）
LONG_MSG_TEMPLATES = [
    "今天真是太累了，早上开会开到中午，下午又处理了一堆紧急的事情，晚上还要加班写报告，感觉整个人都不好了，不过还好事情都差不多完成了，明天可以轻松一下了",
    "上次说的那个事情我想了很久，觉得还是应该再考虑一下，毕竟这涉及到很多方面的影响，不仅仅是表面看起来那么简单，需要综合考虑各种因素才能做出更好的决定",
    "昨天去看了一场电影，名字叫做《xxx》，讲的是一个关于梦想和坚持的故事，非常感人，强烈推荐你也去看一下，真的很不错，特别是最后的结局让人回味无穷",
    "最近在学习一个新的技能，每天晚上下班后都会花一两个小时来练习，虽然进度比较慢，但是感觉还是很有收获的，希望能坚持下去吧，毕竟技多不压身嘛",
    "上周去体检了，医生说身体各方面都还不错，就是有点亚健康，建议我多运动、少熬夜，现在正在努力调整作息时间，争取每天11点前睡觉，希望能坚持下去吧",
    "最近发现了一家很好的餐厅，在xx路那边，环境非常好，菜品也很不错，特别是他们家的招牌菜简直太好吃了，有机会的话我请你去尝尝，绝对不会让你失望的",
    "这个项目终于完成了，前后加起来一共花了三个月的时间，中间遇到了很多困难和问题 好在最后都解决了，虽然过程比较辛苦，但是学到了很多东西还是很值得的",
    "我想和你聊聊关于未来规划的事情，我觉得我们应该认真考虑一下以后的发展方向了，不能总是这样得过且过，毕竟时间不等人啊，你说呢",
    "昨天发生了一件很有意思的事情，下班的时候在地铁上遇到一个很久没见的老同学，聊了一路才发现原来我们住同一个小区，真是太巧了 世界有时候就是这么大又这么小",
    "最近在工作上遇到了一些瓶颈，感觉自己的能力和经验还不够，需要学习的东西还有很多，有时候真的会怀疑自己是不是适合做这行 但是又不想轻易放弃",
    "下周我要出差去北京，大概需要三四天的时间，这次去主要是参加一个重要的会议，如果顺利的话可能还会顺便拜访几个客户，争取把事情都安排好吧",
    "你家附近有没有什么好的健身房？我想办个健身卡锻炼身体，但是对那边不熟悉，你能不能给我推荐一下？或者下次一起健身也可以啊",
    "今天是你的生日吧？祝你生日快乐！虽然不能当面庆祝，但是心意一定要送到，希望新的一岁你能越来越帅/漂亮，工作顺利，爱情甜蜜",
    "下个月我就要搬家了，新房子在xx区，离你那边比较近，到时候欢迎你来玩啊，地方比现在大多了，可以一起吃饭聊天，想想就很开心",
    "最近在学做菜，照着视频学了好几个菜式，今天试着做了一次，虽然卖相不怎么样但是味道居然还可以，看来我还是很有天赋的嘛，下次做给你尝尝"
]

def random_amount(min_val=1, max_val=10000):
    """生成随机金额"""
    return random.randint(min_val, max_val)

def random_time():
    """生成随机时间（2022-2025年）"""
    start = datetime(2022, 1, 1)
    end = datetime(2025, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)

def generate_message():
    """生成一条消息"""
    sender = random.choice(MEMBERS)
    timestamp = random_time().strftime("%Y-%m-%d %H:%M:%S")

    # 50%转账/红包，50%日常
    if random.random() < 0.5:
        # 转账/红包
        template = random.choice(TRANSFER_TEMPLATES)
        if "{amount}" in template:
            amount = random_amount(1, 10000) if "转账" in template else random_amount(1, 500)
            content = template.format(amount=amount)
        else:
            content = template
    else:
        # 日常消息 - 50%短消息，50%长消息
        if random.random() < 0.5:
            content = random.choice(SHORT_MSG_TEMPLATES)
        else:
            content = random.choice(LONG_MSG_TEMPLATES)

    return f'''<div class="chat-item">
    <span class="time">{timestamp}</span>
    <span class="sender">{sender}</span>
    <p class="content">{content}</p>
</div>
'''

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="生成模拟聊天记录HTML文件")
    parser.add_argument(
        "--size-mb",
        type=int,
        default=DEFAULT_TARGET_SIZE_MB,
        help=f"目标文件大小（MB），默认 {DEFAULT_TARGET_SIZE_MB}"
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"输出文件路径，默认 {DEFAULT_OUTPUT_FILE}"
    )
    return parser.parse_args()


def generate_html(output_file: str, target_size_mb: int):
    """生成HTML文件"""
    print(f"开始生成{target_size_mb}MB聊天记录...")

    # 先随机打乱成员
    random.shuffle(MEMBERS)

    target_bytes = target_size_mb * 1024 * 1024

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入HTML头部
        f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>聊天记录</title>
</head>
<body>
''')

        current_size = 0
        message_count = 0

        # 分块生成，每块1000条消息
        while current_size < target_bytes:
            chunk = ""
            for _ in range(1000):
                chunk += generate_message()

            f.write(chunk)
            current_size += len(chunk.encode('utf-8'))
            message_count += 1000

            # 每生成1万条打印一次进度
            if message_count % 10000 == 0:
                progress = current_size / target_bytes * 100
                print(f"已生成 {message_count} 条消息，{current_size/1024/1024:.1f}MB ({progress:.1f}%)")

        # 写入HTML尾部
        f.write('''</body>
</html>
''')

    final_size = os.path.getsize(output_file)
    print(f"完成！共生成 {message_count} 条消息，文件大小 {final_size/1024/1024:.2f}MB")
    print(f"文件保存为: {output_file}")

if __name__ == "__main__":
    args = parse_args()
    generate_html(args.output, args.size_mb)
