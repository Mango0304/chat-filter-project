# Chat Filter - 聊天记录筛选导出工具

一款用于从聊天记录HTML文件中筛选并导出特定消息的工具。支持命令行和图形界面两种使用方式。

## 功能特性

- 🔍 **多模式匹配**: 支持精确匹配和模糊匹配
- 📋 **灵活规则**: 支持任意关键词匹配和全部关键词匹配
- 📄 **多种格式**: 支持导出为 HTML 和 PDF 格式
- ⚡ **大文件支持**: 流式读取处理大型聊天记录文件
- 🖥️ **双界面**: 提供 CLI 命令行和 macOS SwiftUI 图形界面

## 项目结构

```
chat-filter-project/
├── core/                          # Python核心模块
├── ui/                            # SwiftUI 图形界面
├── tests/                         # Python 测试
├── scripts/                       # 开发/构建脚本
│   ├── build_app.sh
│   └── generate_50mb_chat.py
├── packaging/pyinstaller/         # PyInstaller 配置
│   ├── chat_filter.spec
│   ├── ChatFilterBinary.spec
│   └── startup.py
├── samples/                       # 示例输入/输出
│   ├── test_chat.html
│   ├── test_output.html
│   └── generated/                 # 大文件生成目录（默认忽略）
├── resources/fonts/               # PDF 导出字体
├── requirements.txt               # 运行时依赖
├── requirements-dev.txt           # 开发依赖
└── README.md
```

## 各模块功能说明

### 核心模块 (core/)

| 模块 | 功能描述 |
|------|----------|
| `file_reader.py` | 大文件流式读取器，支持分块读取和一次性读取，适用于处理大型聊天记录文件 |
| `parser.py` | HTML解析器，解析聊天记录HTML格式，提取时间、发送者、内容信息 |
| `matcher.py` | 关键词匹配器，支持精确/模糊匹配模式，任意/全部匹配规则 |
| `exporter.py` | 导出器，生成美观的HTML页面，支持导出为PDF格式 |
| `chat_filter.py` | 主入口模块，整合各模块功能，提供CLI命令行接口 |

### 图形界面 (ui/)

| 文件 | 功能描述 |
|------|----------|
| `ChatFilterApp.swift` | SwiftUI应用入口，配置窗口属性 |
| `FilterViewModel.swift` | 视图模型，处理业务逻辑，调用Python核心模块 |
| `ContentView.swift` | 主界面，包含设置面板、日志显示、结果摘要 |

## 安装依赖

### Python 依赖

```bash
cd chat-filter-project
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt  # 可选：开发/测试
```

PDF 导出使用 `reportlab`，已包含在 `requirements.txt` 中，无需额外安装 wkhtmltopdf。

## 使用方法

### 方法一：命令行界面 (CLI)

#### 基本用法

```bash
python3 -m core.chat_filter --input <输入文件> --keywords <关键词> --output <输出文件>
```

#### 参数说明

| 参数 | 简写 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--input` | `-i` | ✅ | 输入的聊天HTML文件路径 | - |
| `--keywords` | `-k` | ✅ | 关键词列表，用逗号分隔 | - |
| `--output` | `-o` | ✅ | 输出文件路径 (.html 或 .pdf) | - |
| `--mode` | `-m` | ❌ | 匹配模式: `exact`精确匹配, `fuzzy`模糊匹配 | `fuzzy` |
| `--rule` | `-r` | ❌ | 匹配规则: `any`任意关键词匹配, `all`所有关键词匹配 | `any` |
| `--chunk-size` | - | ❌ | 文件读取块大小 (字节) | 4194304 (4MB) |
| `--show-keywords` | - | ❌ | 在输出中显示匹配的关键词 | false |

#### 匹配模式说明

- **exact (精确匹配)**: 区分大小写，文本中包含关键词即匹配
- **fuzzy (模糊匹配)**: 不区分大小写，包含关键词即匹配

#### 匹配规则说明

- **any (任意匹配)**: 消息中包含任意一个关键词即匹配
- **all (全部匹配)**: 消息中必须包含所有关键词才匹配

#### 使用示例

**示例1：基本模糊匹配**

```bash
python3 -m core.chat_filter \
    --input chat.html \
    --keywords "借款,转账" \
    --output result.html
```

**示例2：精确匹配**

```bash
python3 -m core.chat_filter \
    --input chat.html \
    --keywords "Hello" \
    --mode exact \
    --output result.html
```

**示例3：全部关键词匹配**

```bash
python3 -m core.chat_filter \
    --input chat.html \
    --keywords "借款,还款" \
    --rule all \
    --output result.html
```

**示例4：导出PDF并显示匹配关键词**

```bash
python3 -m core.chat_filter \
    --input chat.html \
    --keywords "借款,转账,红包" \
    --output result.pdf \
    --show-keywords
```

**示例5：完整命令**

```bash
python3 -m core.chat_filter \
    --input /path/to/chat.html \
    --keywords "借款,转账,还款,汇款" \
    --mode fuzzy \
    --rule any \
    --output /path/to/output.pdf \
    --show-keywords
```

---

### 方法二：图形界面 (UI)

#### 启动应用

```bash
cd chat-filter-project/ui
open ChatFilterApp.swift
# 或者使用 Xcode 打开项目
open ChatFilterApp.xcodeproj
```

#### 界面说明

```
┌─────────────────────────────────────────────────────────────────┐
│  🟢 聊天记录筛选导出工具                              [处理中...] │
├─────────────────────────────────────────────────────────────────┤
│ 输入文件  │  ┌─────────────────────────────────────────┐ [📁]  │
│           │  │ chat.html                               │       │
│           │  └─────────────────────────────────────────┘       │
│           │                                                       │
│ 关键词    │  ┌─────────────────────────────────────────┐        │
│           │  │ 借款, 转账                                │        │
│           │  └─────────────────────────────────────────┘        │
│           │  例如: 借款, 转账, 红包                               │
│           │                                                       │
│ 匹配模式  │  [模糊匹配] [精确匹配]                               │
│           │  模糊匹配: 包含关键词即可                             │
│           │                                                       │
│ 匹配规则  │  [任意匹配] [全部匹配]                                │
│           │  任意关键词匹配即可                                   │
│           │                                                       │
│ 输出文件  │  ┌─────────────────────────────────────────┐ [📁]  │
│           │  │ chat_filtered.html                      │       │
│           │  └─────────────────────────────────────────┘       │
│           │  [HTML] [PDF]                                       │
│           │                                                       │
│           │  ┌─────────────────────────────────────────┐       │
│           │  │           开始筛选                        │       │
│           │  └─────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────────┤
│ 执行日志  │ [🗑️]                                                │
├─────────────────────────────────────────────────────────────────┤
│ [10:00:00] 正在验证输入文件: chat.html                          │
│ [10:00:00] 加载关键词: ['借款', '转账']                        │
│ [10:00:00] 匹配模式: fuzzy, 匹配规则: any                      │
│ [10:00:00] 正在解析聊天记录...                                  │
│ [10:00:00] 共解析 1000 条消息                                   │
│ [10:00:01] 正在进行关键词匹配...                                │
│ [10:00:01] 匹配到 25 条消息                                     │
│ [10:00:01] 正在导出结果到: chat_filtered.html                   │
│ [10:00:01] 完成! 共筛选 25/1000 条消息                         │
├─────────────────────────────────────────────────────────────────┤
│ 总消息: 1000   匹配消息: 25   输出文件: chat_filtered.html      │
└─────────────────────────────────────────────────────────────────┘
```

#### 操作步骤

1. **选择输入文件**: 点击 📁 按钮选择聊天记录HTML文件
2. **输入关键词**: 在文本框中输入关键词，多个关键词用逗号分隔
3. **设置匹配模式**: 选择"模糊匹配"或"精确匹配"
4. **设置匹配规则**: 选择"任意匹配"或"全部匹配"
5. **选择输出文件**: 点击 📁 按钮选择输出位置，或手动输入文件名
6. **选择输出格式**: 选择 HTML 或 PDF 格式
7. **开始筛选**: 点击"开始筛选"按钮
8. **查看结果**: 完成后可以在日志区域查看详情，点击"在Finder中显示"打开输出文件

## HTML输入格式要求

工具期望的HTML格式如下：

```html
<div class="chat-item">
    <span class="time">2024-01-01 10:00:00</span>
    <span class="sender">张三</span>
    <p class="content">消息内容</p>
</div>
<div class="chat-item">
    <span class="time">2024-01-01 11:00:00</span>
    <span class="sender">李四</span>
    <p class="content">借款5000元</p>
</div>
```

## 运行测试

```bash
cd chat-filter-project
python3 -m pytest tests/ -v
```

### 测试覆盖

| 测试文件 | 测试内容 |
|----------|----------|
| `test_file_reader.py` | 文件读取器测试：读取小文件、分块读取、文件不存在、大小计算 |
| `test_parser.py` | 解析器测试：基本解析、单条解析、HTML清理、空文件、消息计数 |
| `test_matcher.py` | 匹配器测试：模糊/精确匹配、任意/全部规则、匹配信息获取 |
| `test_exporter.py` | 导出器测试：HTML导出、匹配信息、HTML转义、保存文件 |
| `test_integration.py` | 集成测试：完整工作流、大文件流式处理 |

## 常见问题

### Q: 为什么PDF导出失败？

A: 本项目 PDF 导出依赖 `reportlab`，请确认依赖已安装：
```bash
python3 -m pip show reportlab
```

### Q: 如何处理超大型聊天记录文件？

A: CLI 支持通过 `--chunk-size` 参数调整块大小，默认4MB足够大多数场景使用。

### Q: 模糊匹配和精确匹配有什么区别？

A: 
- **模糊匹配**: 不区分大小写，只要发送者或消息内容包含关键词即可
- **精确匹配**: 区分大小写，只要发送者或消息内容包含关键词即可

### Q: 可以同时搜索发送者和消息内容吗？

A: 可以。工具默认同时搜索发送者和消息内容。例如搜索"张三"，则发送者为"张三"或消息内容包含"张三"的消息都会被匹配。

## 许可证

MIT License
