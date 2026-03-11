"""HTML生成 + PDF导出模块"""

import os
from typing import List, Optional
from datetime import datetime
from .parser import ChatMessage


class ChatExporter:
    """聊天记录导出器"""

    # HTML模板
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .header .meta {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #eee;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .messages {{
            padding: 20px;
        }}
        .message {{
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
        }}
        .message:nth-child(even) {{
            background-color: #f0f2f5;
        }}
        .message-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        .message-sender {{
            font-weight: bold;
            color: #333;
        }}
        .message-time {{
            color: #888;
        }}
        .message-content {{
            color: #444;
            word-wrap: break-word;
        }}
        .message-keywords {{
            margin-top: 8px;
            font-size: 12px;
            color: #667eea;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="meta">导出时间: {export_time}</div>
        </div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_count}</div>
                <div class="stat-label">筛选消息数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{keywords_display}</div>
                <div class="stat-label">关键词</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{mode_display}</div>
                <div class="stat-label">匹配模式</div>
            </div>
        </div>
        <div class="messages">
            {messages_html}
        </div>
        <div class="footer">
            由 Chat Filter 工具导出
        </div>
    </div>
</body>
</html>
"""

    MESSAGE_TEMPLATE = """<div class="message">
    <div class="message-header">
        <span class="message-sender">{sender}</span>
        <span class="message-time">{time}</span>
    </div>
    <div class="message-content">{content}</div>
    {keywords_html}
</div>"""

    def __init__(self, output_path: Optional[str] = None):
        """
        初始化导出器

        Args:
            output_path: 输出PDF路径，如果为None则只生成HTML
        """
        self.output_path = output_path

    def export(
        self,
        messages: List[ChatMessage],
        keywords: List[str],
        mode: str,
        matched_info: Optional[List[dict]] = None
    ) -> str:
        """
        导出消息到HTML/PDF

        Args:
            messages: 要导出的消息列表
            keywords: 关键词列表
            mode: 匹配模式
            matched_info: 每个消息的匹配信息列表

        Returns:
            str: 生成的HTML内容
        """
        title = "聊天记录筛选结果"
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_count = len(messages)
        keywords_display = ",".join(keywords[:3]) + ("..." if len(keywords) > 3 else "")
        mode_display = "模糊" if mode == "fuzzy" else "精确"

        # 生成消息HTML
        messages_html = self._generate_messages_html(messages, matched_info)

        # 填充模板
        html_content = self.HTML_TEMPLATE.format(
            title=title,
            export_time=export_time,
            total_count=total_count,
            keywords_display=keywords_display,
            mode_display=mode_display,
            messages_html=messages_html
        )

        # 如果指定了输出路径
        if self.output_path:
            # 根据文件扩展名决定输出格式
            if self.output_path.lower().endswith('.pdf'):
                # 准备 PDF 所需的数据结构
                pdf_data = {
                    'title': title,
                    'export_time': export_time,
                    'total_count': total_count,
                    'keywords_display': keywords_display,
                    'mode_display': mode_display,
                    'messages': messages,
                    'matched_info': matched_info
                }
                self._save_pdf_with_data(pdf_data)
            else:
                # 保存为HTML文件
                with open(self.output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"HTML saved to: {self.output_path}")

        return html_content

    def _generate_messages_html(
        self,
        messages: List[ChatMessage],
        matched_info: Optional[List[dict]] = None
    ) -> str:
        """
        生成消息列表HTML

        Args:
            messages: 消息列表
            matched_info: 匹配信息列表

        Returns:
            str: HTML片段
        """
        html_parts = []

        for i, message in enumerate(messages):
            # 获取匹配关键词
            keywords_html = ""
            if matched_info and i < len(matched_info):
                info = matched_info[i]
                if info.get("matched_keywords"):
                    kw_str = ", ".join(info["matched_keywords"])
                    keywords_html = f'<div class="message-keywords">匹配关键词: {kw_str}</div>'

            message_html = self.MESSAGE_TEMPLATE.format(
                sender=self._escape_html(message.sender),
                time=self._escape_html(message.time),
                content=self._escape_html(message.content),
                keywords_html=keywords_html
            )
            html_parts.append(message_html)

        return "\n".join(html_parts)

    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _save_pdf_with_data(self, pdf_data: dict) -> None:
        """使用 ReportLab 保存为 PDF (带完整数据)"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 注册支持中文的字体 (macOS)
        font_name = 'Helvetica'

        # 尝试多个字体路径
        import sys
        import os

        if getattr(sys, 'frozen', False):
            # PyInstaller 打包后的路径
            base_path = sys._MEIPASS
            font_paths = [
                os.path.join(base_path, 'fonts', 'STHeiti Medium.ttc'),
                os.path.join(base_path, 'fonts', 'STHeiti Medium.ttf'),
            ]
        else:
            # 开发环境路径：优先使用项目目录的字体
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            font_paths = [
                os.path.join(script_dir, '..', 'resources', 'fonts', 'STHeiti Medium.ttc'),
                os.path.join(script_dir, '..', 'resources', 'fonts', 'STHeiti Light.ttc'),
                '/System/Library/Fonts/STHeiti Medium.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
            ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_name = 'ChineseFont'
                    break
                except Exception as e:
                    print(f"Font registration warning: {e}")
                    continue

        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()

        # 自定义样式 - 使用中文字体
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            spaceAfter=10,
            alignment=1
        )

        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=12,
            spaceAfter=8,
            textColor=colors.HexColor('#667eea')
        )

        normal_style = ParagraphStyle(
            'Normal',
            fontName=font_name,
            fontSize=10
        )

        message_style = ParagraphStyle(
            'Message',
            fontName=font_name,
            fontSize=9,
            spaceAfter=8,
            wordWrap='CJK'  # 支持中文换行
        )

        story = []

        # 标题
        story.append(Paragraph(pdf_data['title'], title_style))

        # 元信息
        story.append(Paragraph(f"导出时间: {pdf_data['export_time']}", normal_style))
        story.append(Spacer(1, 10))

        # 统计信息表格
        stats_data = [
            ['筛选消息数', '关键词', '匹配模式'],
            [str(pdf_data['total_count']), pdf_data['keywords_display'], pdf_data['mode_display']]
        ]
        stats_table = Table(stats_data, colWidths=[50*mm, 80*mm, 40*mm])
        # 表头使用粗体
        if font_name == 'Helvetica':
            table_font = 'Helvetica-Bold'
        else:
            # 对于注册的中文字体，使用相同字体（ReportLab 会自动选择粗体）
            table_font = font_name
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), table_font),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 15))

        # 消息列表标题
        story.append(Paragraph("筛选消息列表", heading_style))
        story.append(Spacer(1, 10))

        # 消息内容
        messages = pdf_data['messages']
        matched_info = pdf_data.get('matched_info', [])

        for i, msg in enumerate(messages):
            # 消息头
            msg_header = f"<b>{self._escape_for_pdf(msg.sender)}</b> - {self._escape_for_pdf(msg.time)}"
            story.append(Paragraph(msg_header, normal_style))

            # 消息内容
            content = self._escape_for_pdf(msg.content)
            story.append(Paragraph(content, message_style))

            # 匹配关键词
            if matched_info and i < len(matched_info):
                info = matched_info[i]
                if info.get('matched_keywords'):
                    kw_str = ', '.join(info['matched_keywords'])
                    story.append(Paragraph(
                        f"<i>匹配关键词: {kw_str}</i>",
                        ParagraphStyle('Keyword', fontName=font_name, fontSize=8, textColor=colors.HexColor('#667eea'))
                    ))

            story.append(Spacer(1, 8))

        # 生成 PDF
        doc.build(story)
        print(f"PDF saved to: {self.output_path}")

    def _escape_for_pdf(self, text: str) -> str:
        """转义 PDF 特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def save_html(self, html_content: str, output_path: str) -> None:
        """保存HTML文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML saved to: {output_path}")
