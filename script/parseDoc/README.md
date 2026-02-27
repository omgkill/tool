# ParseDoc - 网页文档解析工具

一个用于解析网页文档、提取单词并进行词形还原的 Python 工具。支持单页面解析和多页面爬虫模式，采用管道式架构设计。

## 功能特性

- **管道式架构**：模块化设计，各模块职责清晰，易于扩展
- **多线程并行**：100线程并发爬取，显著提高性能
- **智能爬虫**：URL去重、域名限制、深度限制
- **NLP处理**：基于spaCy的词形还原、停用词过滤
- **多格式输出**：JSON、TXT、PDF
- **灵活配置**：支持配置化，可跳过不需要的处理步骤
- **有序输出**：输出文件按时间戳命名，自动保存到output目录

## 项目结构

```
parseDoc/
├── app_pipeline.py              # 入口文件
├── parser_service/              # 核心服务模块
│   ├── pipeline/                # 管道控制器
│   │   ├── __init__.py
│   │   └── pipeline.py          # 协调各模块工作
│   ├── crawler/                 # 爬虫模块
│   │   ├── __init__.py
│   │   ├── link_extractor.py    # 链接提取
│   │   └── spider.py            # 爬虫调度器
│   ├── extractor/               # HTML解析模块
│   │   ├── __init__.py
│   │   └── extractor.py         # 提取文本、标题
│   ├── processor/               # NLP处理模块
│   │   ├── __init__.py
│   │   └── processor.py         # 清洗、分段、词形还原
│   ├── output/                  # 输出模块
│   │   ├── __init__.py
│   │   ├── base_output.py       # 输出基类
│   │   ├── json_output.py       # JSON输出
│   │   ├── txt_output.py        # TXT输出
│   │   └── pdf_output.py        # PDF输出
│   ├── fetcher/                 # 网页获取模块
│   │   ├── __init__.py
│   │   └── web_fetcher.py       # HTTP请求、代理
│   ├── cleaner/                 # 文本清洗模块
│   │   ├── __init__.py
│   │   └── text_cleaner.py
│   └── nlp/                     # NLP基础模块
│       ├── __init__.py
│       ├── lemmatizer.py        # 词形还原
│       └── splitter.py          # 文本分段
├── output/                      # 输出目录（自动创建）
│   ├── 20260226_164500_output.json      # JSON格式输出
│   ├── 20260226_164500_words.txt        # 单词列表（按词频排序）
│   └── 20260226_164500_documents.pdf    # PDF文档
├── requirements.txt             # 依赖列表
├── README.md                    # 说明文档
├── MODIFICATION_LOG.md          # 修改记录
└── PARALLEL_CRAWLER_FLOWCHART.md # 并行爬虫流程图
```

## 架构说明

### 管道式架构

```
┌─────────────────────────────────────────────────┐
│                  Pipeline 控制器                         │
└─────────────────────────────────────────────────┘
                          ↓
    ┌─────────┴─────────┐
    ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  爬虫模块    │  │  解析模块    │  │  NLP处理模块  │  │  输出模块    │
│ (Crawler)   │  │ (Extractor)  │  │ (Processor)   │  │ (Output)    │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**优势：**
- **灵活性**：可以根据需求组合不同的处理步骤
- **可维护性**：每个模块职责单一，易于维护和测试
- **可扩展性**：可以轻松添加新的处理步骤或输出格式
- **性能优化**：可以跳过不需要的步骤，提高速度

## 安装

### 1. 安装依赖

```bash
py -3.11 -m pip install -r requirements.txt
```

### 2. 下载 spaCy 语言模型

```bash
py -3.11 -m spacy download en_core_web_sm
```

### 3. 代理配置（可选）

默认使用代理 `http://127.0.0.1:10809`，可在 `web_fetcher.py` 中修改：

```python
# 修改代理端口
WebFetcher(proxy_port=10809)

# 禁用代理
fetcher.disable_proxy()
```

## 使用方法

### 命令行使用

```bash
# 爬取指定数量的页面
py -3.11 app_pipeline.py crawl https://go.dev/doc/ 10

# 爬取默认50个页面
py -3.11 app_pipeline.py crawl https://go.dev/doc/
```

### 代码调用

```python
from parser_service.pipeline.pipeline import Pipeline

# 创建管道
config = {
    'max_pages': 10,
    'max_workers': 100
}
pipeline = Pipeline(config)

# 运行管道
result = pipeline.run('https://go.dev/doc/')

print(f"处理文档数: {len(result['documents'])}")
print(f"唯一单词数: {len(result['global_unique_words'])}")
```

## 输出文件

### 输出目录结构

所有输出文件自动保存到 `output/` 目录，文件名包含时间戳：

```
output/
├── 20260226_164500_output.json      # JSON格式输出
├── 20260226_164500_words.txt        # 单词列表（按词频排序）
└── 20260226_164500_documents.pdf    # PDF文档
```

### JSON 输出 - 关系型结构

便于后续扩展 MySQL 数据库，避免数据重复：

```json
{
  "metadata": {
    "source_url": "https://go.dev/doc/",
    "crawled_at": "2026-02-26T16:45:00",
    "total_documents": 10,
    "total_unique_words": 595
  },
  "words": [
    {"id": 0, "lemma": "ability"},
    {"id": 1, "lemma": "abstract"}
  ],
  "documents": [
    {"id": 1, "url": "https://go.dev/doc/effective_go", "title": "Effective Go", "depth": 1}
  ],
  "paragraphs": [
    {"id": 0, "doc_id": 1, "text": "段落文本", "para_index": 0}
  ],
  "sentences": [
    {"id": 0, "para_id": 0, "text": "句子文本"}
  ],
  "word_occurrences": [
    {"id": 0, "sent_id": 0, "word_id": 0, "original": "running", "pos": "VERB"}
  ]
}
```

**关系说明：**
- `documents` → `paragraphs` (通过 doc_id)
- `paragraphs` → `sentences` (通过 para_id)
- `sentences` → `word_occurrences` (通过 sent_id)
- `word_occurrences` → `words` (通过 word_id)

### TXT 输出 - 纯单词列表

每行一个单词，按词频从高到低排列：

```
go
package
function
...
```

### PDF 输出 - 文档内容

包含：
- 文档元数据（源URL、爬取时间、总文档数、总唯一单词数）
- 每个文档的完整文本内容
- 全局唯一单词列表（按词频排序）

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_pages` | 最大页面数限制 | 50 |
| `max_workers` | 线程池大小 | 100 |
| `delay` | 请求间隔（秒） | 0.1 |
| `nlp_enabled` | 是否启用NLP处理 | True |
| `output_formats` | 输出格式列表 | ['json', 'txt', 'pdf'] |
| `output_dir` | 输出目录 | 'output' |

## 依赖说明

| 库 | 用途 |
|---|---|
| requests | HTTP 请求，获取网页内容 |
| beautifulsoup4 | HTML 解析，提取文本 |
| spacy | 自然语言处理，词形还原 |
| lxml | 更快的HTML解析 |
| reportlab | PDF生成 |

## 性能特点

- **多线程并行**：使用ThreadPoolExecutor，100线程并发处理
- **真正的并行**：一次性提交所有任务，真正并行执行
- **线程安全**：使用锁保护共享数据，避免并发冲突
- **进度显示**：实时显示处理进度
- **有序输出**：文件名带时间戳，便于管理

## 注意事项

1. 首次运行前必须下载 spaCy 模型
2. 默认使用代理 `http://127.0.0.1:10809`，如需修改请编辑 `web_fetcher.py`
3. 支持英文文档处理
4. 爬虫默认有请求间隔，避免被封
5. PDF输出包含文档的文本内容，适合阅读
6. 输出文件自动保存到 `output/` 目录

## 更新日志

详见 [MODIFICATION_LOG.md](MODIFICATION_LOG.md)

## 架构图

详见 [PARALLEL_CRAWLER_FLOWCHART.md](PARALLEL_CRAWLER_FLOWCHART.md)